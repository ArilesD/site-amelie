import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import model.db as db
from io import BytesIO
import base64
from textwrap import fill


def graphique(annee):
    data = db.montant_moyen_prescriptions(annee)
    if data.empty:
        return None

    postes = [fill(label, width=32) for label in data["libelle_poste_prescription"]]
    figure = Figure(figsize=(9, 5.5), layout="constrained")
    ax = figure.subplots()
    ax.barh(postes, data["montant_moyen"] / 1_000, color="#19588B")
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.2)
    ax.set_xlabel("Montant moyen en milliers d’euros")
    ax.set_title(f"Montants moyens en France en {annee}")
    return image_png(figure)


def graphique_montants_region(annee):
    data = db.comparaison_prescriptions_par_region(annee)
    if data.empty:
        return None

    montants = data["prescriptions_totales"] / 1_000_000
    regions = data["region"].replace("Ile-de-France", "Île-de-France")
    figure = Figure(figsize=(9, max(3, len(data) * 0.36 + 1.3)), layout="constrained")
    ax = figure.subplots()
    ax.barh(regions, montants, color="#19588B")
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.2)
    ax.set_xlabel("Montant en millions d’euros")
    ax.set_title(f"Prescriptions par région en {annee}")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda value, _: f"{value:,.0f}".replace(",", " ")))
    return image_png(figure)


def image_png(figure):
    with BytesIO() as image:
        figure.savefig(image, format="png")
        return "data:image/png;base64," + base64.b64encode(image.getvalue()).decode("ascii")
