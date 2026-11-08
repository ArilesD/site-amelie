# Ameli - Application web d’exploration des données

Projet universitaire réalisé en équipe. Cette application Flask prolonge la [conception de la base Ameli](https://github.com/ArilesD/database-amelie). Elle permet d’explorer des données agrégées de l’Assurance maladie à partir d’une base SQLite.

- Filtrer les effectifs de professions de santé par région et profession.
- Consulter une sélection de prescriptions et la filtrer par année.
- Visualiser le montant des prescriptions à l’aide de graphiques Matplotlib.

## Démarrer en local

Avec Python 3.12, crée puis active un environnement virtuel depuis la racine du dépôt.

```bash
python -m venv .venv
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS ou Linux
source .venv/bin/activate
```

Installe les dépendances, prépare la base et lance Flask.

```bash
python -m pip install -r requirements.txt
python prepare_data.py
python -m flask --app app run
```

Ouvre [http://127.0.0.1:5000](http://127.0.0.1:5000). La préparation extrait la base SQLite d’environ 278 Mo depuis `site-amelie.zip`. L’archive contient l’état d’origine du projet. La version de la base attendue par le site est celle de cette archive.

## Lire le code

| Fichier ou dossier | Rôle |
| --- | --- |
| `app.py` | Pages Flask, filtres et restitution des résultats. |
| `model/db.py` | Requêtes SQLite et chargement des résultats avec pandas. |
| `utils/graphiques.py` | Graphiques construits à partir des requêtes. |
| `templates/` et `static/` | Pages HTML et styles. |

[Rapport du projet](Rapport.pdf) · [Source des données Ameli](https://data.ameli.fr/)
