"""Extraire les données de la démonstration depuis la base SQLite du projet."""

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

REGIONS = (4, 11, 32, 84, 99)
DEPARTEMENTS = (59, 69, 93, 974, 999)
ANNEES = (2022, 2023)


def creer_extrait(source, destination):
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(destination)

    with closing(sqlite3.connect(":memory:", uri=True)) as extrait:
        extrait.execute("ATTACH DATABASE ? AS origine", (source.as_uri() + "?mode=ro",))
        tables = {
            "Regions": ("Id_Region IN (?,?,?,?,?)", REGIONS),
            "Departements": ("Num_Departement IN (?,?,?,?,?)", DEPARTEMENTS),
            "ProfessionsSante": ("1", ()),
            "Prescriptions": (
                "Annee IN (?,?) AND Id_Region IN (?,?,?,?,?) "
                "AND Num_Departement IN (?,?,?,?,?) AND Profession_sante = ?",
                ANNEES + REGIONS + DEPARTEMENTS + ("Ensemble des médecins",),
            ),
            "Demographie": (
                "Annee = ? AND Id_Region IN (?,?,?,?) AND Num_Departement = 999",
                (max(ANNEES), *REGIONS[:-1]),
            ),
        }
        for table, (filtre, params) in tables.items():
            schema = extrait.execute(
                "SELECT sql FROM origine.sqlite_master WHERE type = 'table' AND name = ?",
                (table,),
            ).fetchone()[0]
            extrait.execute(schema)
            extrait.execute(f"INSERT INTO {table} SELECT * FROM origine.{table} WHERE {filtre}", params)

        # Le code 999 de la dimension Département désigne les agrégats territoriaux.
        extrait.execute("INSERT INTO Regions VALUES (999, 'Tout département')")
        if extrait.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Référence manquante dans l’extrait")
        extrait.commit()
        with closing(sqlite3.connect(destination)) as sortie:
            extrait.backup(sortie, name="main")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    arguments = parser.parse_args()
    creer_extrait(arguments.source, arguments.destination)
