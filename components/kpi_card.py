"""
components/kpi_card.py
======================
Composant d'affichage d'un indicateur clé institutionnel (KPI) :
- Titre / libellé
- Valeur mise en valeur avec unité
- Période de référence / Source
- Interprétation analytique issue des données
- Code couleur sémantique
"""

from dash import html

def create_kpi_card(label, value, period, interpretation, domain="bleu"):
    """
    domain : 'bleu', 'violet', 'vert', 'jaune', 'rouge'
    """
    return html.Div(
        className=f"kpi-card {domain}",
        children=[
            html.Div(label, className="kpi-label"),
            html.Div(
                className="kpi-value-row",
                children=[
                    html.Span(value, className="kpi-value")
                ]
            ),
            html.Div(f"Période : {period}", className="kpi-periode"),
            html.Div(interpretation, className="kpi-interpretation")
        ]
    )
