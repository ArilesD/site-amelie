from contextlib import closing
from pathlib import Path
import pandas as pd
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
BASE_COMPLETE = ROOT / "model" / "data" / "debase_db.sqllite3"
BASE_DEMO = ROOT / "demo" / "amelie-demo.sqlite"
db_path = BASE_COMPLETE if BASE_COMPLETE.is_file() else BASE_DEMO
DEMONSTRATION = db_path == BASE_DEMO

#####################################################################
# FONCTIONS UTILES
#####################################################################

def connect_db():
    """
    Fonction pour se connecter à la base de données.
    Retourne une connexion SQLite.
    """
    return sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True)


def annees_prescriptions():
    with closing(connect_db()) as conn:
        return [row[0] for row in conn.execute("SELECT DISTINCT Annee FROM Prescriptions ORDER BY Annee DESC")]

def visualiser_table():
    """
    Fonction pour visualiser le contenu des prescriptions avec le libellé des départements.
    """
    conn = connect_db()  # Connexion à la base de données

    # Requête SQL pour joindre les tables Prescriptions et Departements
    query = """
    SELECT 
        p.*,
        d.libelle_departement
        
    FROM 
        Prescriptions p
    INNER JOIN 
        Departements d
    ON 
        p.Num_Departement = d.Num_Departement
    ORDER BY p.Id_Prescription
    LIMIT 200;
    
    """
    
    # Exécuter la requête et charger les résultats dans un DataFrame
    result = pd.read_sql_query(query, conn)
    
    # Fermer la connexion à la base de données
    conn.close()
    
    return result







def comparaison_prescriptions_par_region(annee=None):
    """Utilise les totaux régionaux déjà publiés pour l’ensemble des médecins."""
    if annee is None:
        annee = max(annees_prescriptions(), default=None)
    query = """
    SELECT r.libelle_region AS region, p.montant_total_prescription_integer AS prescriptions_totales
    FROM Prescriptions p
    JOIN Regions r ON p.Id_Region = r.Id_Region
    WHERE p.Annee = ?
      AND p.Num_Departement = 999
      AND p.Profession_sante = 'Ensemble des médecins'
      AND p.poste_prescription = 'total'
      AND r.Id_Region <> 99
      AND typeof(p.montant_total_prescription_integer) = 'integer'
    ORDER BY prescriptions_totales, region
    """
    with closing(connect_db()) as conn:
        return pd.read_sql_query(query, conn, params=(annee,))


def montant_moyen_prescriptions(annee=None):
    """Récupère les montants moyens nationaux publiés par poste de prescription."""
    if annee is None:
        annee = max(annees_prescriptions(), default=None)
    query = """
    SELECT libelle_poste_prescription, montant_moyen_prescription_integer AS montant_moyen, Annee
    FROM Prescriptions
    WHERE Annee = ?
      AND Id_Region = 99
      AND Num_Departement = 999
      AND Profession_sante = 'Ensemble des médecins'
      AND poste_prescription <> 'total'
      AND typeof(montant_moyen_prescription_integer) = 'integer'
    ORDER BY poste_prescription
    """
    with closing(connect_db()) as conn:
        return pd.read_sql_query(query, conn, params=(annee,))



def get_profession_names():
    # Connexion à la base de données
    conn = connect_db()

    # Requête SQL pour récupérer toutes les professions
    query = """
    SELECT DISTINCT Profession_sante
    FROM ProfessionsSante
    ORDER BY Profession_sante ASC;

    """
   

    # Exécution de la requête SQL
    professions = pd.read_sql_query(query, conn)

    # Fermeture de la connexion à la base de données
    conn.close()
    return professions

def get_professions_by_region(id_region):
    """Récupère les effectifs régionaux par profession et mode d’exercice."""
    query = """
    SELECT Profession_sante, effectif, libelle_type_exercice_liberal, Annee
    FROM Demographie
    WHERE Id_Region = :region
      AND Num_Departement = 999
      AND Annee = (
          SELECT MAX(Annee) FROM Demographie
          WHERE Id_Region = :region AND Num_Departement = 999
      )
      AND typeof(effectif) = 'integer'
    ORDER BY effectif DESC, Profession_sante, libelle_type_exercice_liberal
    """
    with closing(connect_db()) as conn:
        return pd.read_sql_query(query, conn, params={"region": id_region})


def get_region_name(id_region):
    """Retourne le nom de la région à partir de son ID"""
    region_names = {
        '11': 'Île-de-France',
        '24': 'Centre-Val de Loire',
        '27': 'Bourgogne-Franche-Comté',
        '28': 'Normandie',
        '32': 'Hauts-de-France',
        '44': 'Grand Est',
        '52': 'Pays de la Loire',
        '53': 'Bretagne',
        '75': 'Nouvelle-Aquitaine',
        '76': 'Occitanie',
        '84': 'Auvergne-Rhône-Alpes',
        '93': "Provence-Alpes-Côte d'Azur",
        '94': 'Corse',
        '1': 'Guadeloupe',
        '2': 'Martinique',
        '3': 'Guyane',
        '4': 'La Réunion',
        '6': 'Mayotte'
        
    }
    return region_names.get(str(id_region), f"Région {id_region}")
