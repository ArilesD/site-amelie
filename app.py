from flask import Flask, render_template, request
import model.db as db  
import matplotlib
from utils.graphiques import graphique, graphique_camembert_prescriptions


app = Flask(__name__)
matplotlib.use('Agg')

@app.route('/')
def accueil():
    # Affiche la page d'accueil
    return render_template('index.html')

@app.route('/trie_par_region', methods=['GET', 'POST'])
def trie_par_region():
    if request.method == 'POST':
        # Récupère les données du formulaire
        region_id = request.form.get('region_name')
        profession = request.form.get('profession')
        effectif_min = request.form.get('effectif_min', type=int)
        effectif_max = request.form.get('effectif_max', type=int)
        
        # Récupère les professions et le nom de la région depuis la base de données
        professions = db.get_professions_by_region(region_id)
        region_name = db.get_region_name(region_id)
        
        # Applique les filtres si les données existent
        if professions is not None and not professions.empty:
            if profession:
                professions = professions[professions['Profession_sante'] == profession]
            if effectif_min is not None:
                professions = professions[professions['effectif'] >= effectif_min]
            if effectif_max is not None:
                professions = professions[professions['effectif'] <= effectif_max]
       
        # Retourne la page avec les résultats filtrés
        return render_template('result_professions.html',
                               professions=professions,
                               region_name=region_name,
                               region_id=region_id,
                               selected_profession=profession)
    
    # Affiche le formulaire de recherche
    return render_template('trie_par_region.html')

@app.route('/apropos')
def apropos():
    # Affiche la page "A propos"
    return render_template('apropos.html')

@app.route('/afficher_prescriptions', methods=['GET'])
def afficher_prescriptions():
    # Récupère les paramètres de filtrage
    annee_min = request.args.get('annee_min', type=int)
    annee_max = request.args.get('annee_max', type=int)
    search_query = request.args.get('search', '').lower()
    order_annee = request.args.get('order_annee', default='asc', type=str)

    # Récupère toutes les données des prescriptions
    Prescriptions = db.visualiser_table()

    # Convertit les colonnes nécessaires
    Prescriptions['Id_Prescription'] = Prescriptions['Id_Prescription'].astype(int)
    Prescriptions['Annee'] = Prescriptions['Annee'].astype(int)

    # Filtre par années si les paramètres sont renseignés
    if annee_min:
        Prescriptions = Prescriptions[Prescriptions['Annee'] >= annee_min]
    if annee_max:
        Prescriptions = Prescriptions[Prescriptions['Annee'] <= annee_max]

    # Recherche dans toutes les colonnes
    if search_query:
        Prescriptions = Prescriptions[Prescriptions.apply(
            lambda row: any(search_query in str(val).lower() for val in row.astype(str).values), axis=1)
        ]

    # Trie par année
    if order_annee == 'asc':
        Prescriptions = Prescriptions.sort_values(by='Annee', ascending=True)
    else:
        Prescriptions = Prescriptions.sort_values(by='Annee', ascending=False)

    # Format le montant moyen pour l'affichage
    Prescriptions['montant_moyen_prescription'] = Prescriptions['montant_moyen_prescription'].apply(
        lambda x: f"{float(x):,.0f}".replace(',', ' ') if isinstance(x, (int, float)) else x
    )

    # Retourne la page avec les données filtrées
    return render_template(
        'afficher_prescriptions.html',
        Prescriptions=Prescriptions.drop(columns=['Num_Departement']).to_dict(orient='records'),
        annee_min=annee_min,
        annee_max=annee_max,
        search=search_query,
        order_annee=order_annee
    )

@app.route('/histogramme_prescription', methods=['GET', 'POST'])
def histogramme_prescription():
    # Récupère l'année du formulaire (ou None si non renseignée)
    annee = request.form.get('annee', type=int)
    if not annee:
        annee = None

    # Génère l'image de l'histogramme
    histogram_image = graphique(annee)
    
    # Affiche la page avec le graphique
    return render_template('histogramme_prescription.html', histogram_image=histogram_image)

@app.route('/graphique_prescriptions_region', methods=['GET', 'POST'])
def graphique_prescriptions_region():
    # Récupère l'année depuis le formulaire ou utilise une valeur par défaut
    annee = request.form.get('annee', type=int)
    if not annee:
        annee = 2010

    # Génère le graphique en camembert
    histogram_image = graphique_camembert_prescriptions(annee)
    
    # Affiche la page avec le graphique
    return render_template('graphique_prescriptions_region.html', histogram_image=histogram_image, annee=annee)

if __name__ == "__main__":
    app.run(debug=True)
