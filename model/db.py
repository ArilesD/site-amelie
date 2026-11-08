import os
import pandas as pd
import sqlite3




DATABASE = "debase_db.sqllite3"  # Nom exact du fichier de la base
db_path = os.path.join(os.path.dirname(__file__), 'data', DATABASE)  # Base dans 'data'

#####################################################################
# FONCTIONS UTILES
#####################################################################

def connect_db():
    """
    Fonction pour se connecter à la base de données.
    Retourne une connexion SQLite.
    """
    return sqlite3.connect(db_path)

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
    
    LIMIT 200;
    
    """
    
    # Exécuter la requête et charger les résultats dans un DataFrame
    result = pd.read_sql_query(query, conn)
    
    # Fermer la connexion à la base de données
    conn.close()
    
    return result







def comparaison_prescriptions_par_region(annee=None):
    """
    Fonction pour comparer les régions selon les prescriptions totales en fonction d'une année.
    """
    conn = connect_db()
    query = """
    SELECT r.libelle_region AS region, SUM(p.montant_total_prescription) AS prescriptions_totales
    FROM Prescriptions p
    JOIN Regions r ON p.Id_Region = r.Id_Region
    """
    if annee:
        query += " WHERE p.Annee = ?"
    query += " GROUP BY r.libelle_region;"
    
    params = (annee,) if annee else ()
    result = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return result


def get_professions_by_region(region_id):
    """
    Récupérer les professions et leur effectif dans une région donnée.
    """
    conn = connect_db()
    query = """
    SELECT 
        ps.Profession_sante AS Profession_sante, 
        SUM(d.effectif) AS effectif
    FROM 
        Demographie d
    INNER JOIN 
        ProfessionsSante ps ON d.Profession_sante = ps.Profession_sante
    INNER JOIN 
        Regions r ON d.Id_Region = r.Id_Region
    WHERE 
        r.libelle_region = ?
    GROUP BY 
        ps.Profession_sante
    ORDER BY 
        effectif DESC;
    """
    result = pd.read_sql_query(query, conn, params=(region_id,))
    conn.close()
    return result





def montant_moyen_prescriptions(annee=None):
    """
    Fonction pour évaluer le montant moyen des prescriptions par poste de prescription,
    avec option de filtrage par année.
    """
    conn = connect_db()
    
    # Si une année est spécifiée, ajuster la requête pour filtrer par année
    query = """
    SELECT libelle_poste_prescription, AVG(montant_moyen_prescription_integer) AS montant_moyen, Annee
    FROM Prescriptions
    """
    if annee:
        query += f" WHERE Annee = {annee}"
    
    query += " GROUP BY libelle_poste_prescription;"
    
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result



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
    """
    Fonction pour récupérer les professions présentes dans une région donnée.
    """
    conn = connect_db()
    query = """
    SELECT Profession_sante, SUM(effectif) AS effectif, libelle_type_exercice_liberal
    FROM Demographie
    WHERE Id_Region = ?
    GROUP BY Profession_sante
    ORDER BY effectif DESC
    LIMIT 20;
    """
    result = pd.read_sql_query(query, conn, params=(id_region,))
    conn.close()
    return result
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
