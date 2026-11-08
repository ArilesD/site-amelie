import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import model.db as db
from io import BytesIO
import base64

# Fonction qui genere un graphique en barres pour les montants moyens des prescriptions
def graphique(annee=None):
    # Recuperation des donnees pour une annee specifique ou toutes les annees
    data = db.montant_moyen_prescriptions(annee)

    # On recupere les postes de prescription et les montants moyens
    postes = data['libelle_poste_prescription']
    montants_moyens = data['montant_moyen']

    # On configure le graphique
    plt.figure(figsize=(8, 6), facecolor='white')
    plt.bar(postes, montants_moyens, color='black', edgecolor='black')  # On trace le graphique en barres
    plt.xlabel('Poste de prescription', color='black')  # Etiquette pour l'axe x
    plt.ylabel("Montant moyen des prescriptions (En milliers d'€)", color='black')  # Etiquette pour l'axe y
    plt.xticks(rotation=20, ha='right', color='black')  # On ajuste les etiquettes sur l'axe x
    plt.yticks(color='black')  # Couleur des valeurs sur l'axe y
    plt.grid(axis='y', alpha=0.5, color='gray')  # Ajout d'une grille pour mieux lire les valeurs
    if annee:
        plt.title(f"Montant moyen des prescriptions en France en {annee}", color='black')  # Titre avec l'annee
    else:
        plt.title("Montant moyen des prescriptions", color='black')  # Titre generique
    ax = plt.gca()  # Recuperation de l'objet axe
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1e3:,.0f}'))  # Format des valeurs y
    ax.set_facecolor('#f1f6ff')  # Couleur de fond

    # Sauvegarde du graphique en memoire
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight', facecolor='#f1f6ff')  # Sauvegarde
    plt.close()  # Fermeture du graphique

    # Encodage de l'image en base64
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'  # Retourne l'image encodee

# Fonction qui genere un camembert pour les prescriptions par region
def graphique_camembert_prescriptions(annee=None):
    # Recuperation des donnees pour une annee specifique ou toutes les annees
    data = db.comparaison_prescriptions_par_region(annee)

    # On verifie que les colonnes necessaires sont la
    if 'region' not in data.columns or 'prescriptions_totales' not in data.columns:
        raise KeyError("Les colonnes 'region' et 'prescriptions_totales' sont manquantes dans les donnees.")

    # On enleve les lignes qui contiennent "France"
    data = data[~data['region'].str.contains('France', case=False, na=False)]
    
    # On separe les regions exclues et incluses
    regions_to_exclude = ['Mayotte', 'La Reunion', 'Martinique', 'Guyane', 'Guadeloupe']
    excluded_data = data[data['region'].isin(regions_to_exclude)]
    included_data = data[~data['region'].isin(regions_to_exclude)]
    
    # On recupere les noms de regions et leurs valeurs
    regions_included = included_data['region']
    prescriptions_included = included_data['prescriptions_totales']
    regions_excluded = excluded_data['region']
    prescriptions_excluded = excluded_data['prescriptions_totales']

    # Couleurs pour les camemberts
    custom_colors = ["#D5FFB4", "#B7FF81", "#D0E4FF", "#AED1FF"] * (len(regions_included) // 4 + 1)
    exclude_colors = ["#D5FFB4", "#B7FF81", "#D0E4FF", "#AED1FF","#87af6b"]
    explode = [0.1] * len(regions_included)  # Decalage des parts

    # Creation de la figure
    plt.figure(figsize=(12, 12), facecolor='#121212')
    
    # Premier camembert
    plt.subplot(1, 2, 1)
    plt.pie(
        prescriptions_included,
        labels=regions_included,
        autopct='%1.1f%%',
        explode=explode,
        startangle=140,
        colors=custom_colors[:len(regions_included)],
        textprops={'fontsize': 10, 'color': 'black'},
        wedgeprops={'width': 0.4}
    )

    # Deuxieme camembert
    plt.subplot(1, 2, 2)
    plt.pie(
        prescriptions_excluded,
        labels=regions_excluded,
        autopct='%1.1f%%',
        startangle=140,
        colors=exclude_colors[:len(regions_excluded)],
        textprops={'fontsize': 10, 'color': 'black'},
        wedgeprops={'width': 0.4}
    )

    plt.tight_layout()  # Ajuste les espaces

    # Sauvegarde du graphique en memoire
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight', facecolor='#ffffff00')  # Sauvegarde
    plt.close()  # Ferme la figure

    # Encodage de l'image en base64
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'  # Retourne l'image encodee