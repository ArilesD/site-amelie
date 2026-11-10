from flask import Flask, render_template, request
import model.db as db  
import matplotlib

matplotlib.use('Agg')

from utils.graphiques import graphique, graphique_montants_region

app = Flask(__name__)

@app.route('/')
def accueil():
    # Affiche la page d'accueil
    return render_template('index.html', demonstration=db.DEMONSTRATION)

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
        annee = int(professions['Annee'].iloc[0]) if not professions.empty else None
        
        # Applique les filtres si les données existent
        if not professions.empty:
            if profession:
                professions = professions[professions['Profession_sante'] == profession]
            if effectif_min is not None:
                professions = professions[professions['effectif'] >= effectif_min]
            if effectif_max is not None:
                professions = professions[professions['effectif'] <= effectif_max]
       
        # Retourne la page avec les résultats filtrés
        return render_template('result_professions.html',
                               professions=professions,
                               noms_professions=professions['Profession_sante'].unique(),
                               region_name=region_name,
                               annee=annee,
                               demonstration=db.DEMONSTRATION)
    
    # Affiche le formulaire de recherche
    return render_template('trie_par_region.html', demonstration=db.DEMONSTRATION)

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

    # Récupère un aperçu des prescriptions
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
    if search_query and not Prescriptions.empty:
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
    annees = db.annees_prescriptions()
    annee = request.form.get('annee', default=annees[0] if annees else None, type=int)
    return render_template(
        'histogramme_prescription.html',
        histogram_image=graphique(annee),
        annee=annee,
        annees=annees,
    )

@app.route('/graphique_prescriptions_region', methods=['GET', 'POST'])
def graphique_prescriptions_region():
    annees = db.annees_prescriptions()
    annee = request.form.get('annee', default=annees[0] if annees else None, type=int)
    histogram_image = graphique_montants_region(annee)
    return render_template(
        'graphique_prescriptions_region.html',
        histogram_image=histogram_image,
        annee=annee,
        annees=annees,
        demonstration=db.DEMONSTRATION,
    )

if __name__ == "__main__":
    app.run(debug=True)
