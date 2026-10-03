"""
components/chart_container.py
=============================
Conteneur institutionnel standardisé pour les graphiques et visualisations :
- Question analytique en sous-titre supérieur
- Titre de la visualisation
- Contenu / Graphique
- Mention de la source et notes méthodologiques
"""

from dash import html

def create_chart_box(question, title, chart_component, source, subtitle=None):
    """
    Enveloppe standardisée pour graphique analytique.
    """
    header_children = [
        html.Div(question, className="card-question"),
        html.H3(title, className="card-title")
    ]
    if subtitle:
        header_children.append(html.P(subtitle, className="card-subtitle"))

    return html.Div(
        className="card-box",
        children=[
            html.Div(className="card-header", children=header_children),
            html.Div(chart_component),
            html.Div(
                className="card-footer-source",
                children=[
                    html.Span(f"Source : {source}"),
                    html.Span("Togo Digital Insight - Observatoire national")
                ]
            )
        ]
    )
