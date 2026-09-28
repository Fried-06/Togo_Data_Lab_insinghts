"""
pages/overview.py
=================
Page 1 : Vue d'ensemble — L'inclusion numérique au Togo en un regard.
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from utils.calculations import get_overview_kpis
from utils.data_loader import get_internet_users, get_internet_tech
from utils.theme import COLORS, apply_plotly_theme
from components.kpi_card import create_kpi_card
from components.chart_container import create_chart_box

def create_overview_chart(is_dark=False):
    """Génère la courbe principale d'évolution de l'adoption d'Internet au Togo."""
    users_df = get_internet_users()
    users_recent = users_df[(users_df["annee"] >= 2005) & (users_df["annee"] <= 2022)].sort_values("annee")
    
    tech_df = get_internet_tech()
    pen_df = tech_df[tech_df["indicateur"].str.contains("Toutes technologies", na=False)].sort_values("annee")
    
    fig = go.Figure()
    
    # Série Banque Mondiale / ITU
    fig.add_trace(go.Scatter(
        x=users_recent["annee"],
        y=users_recent["valeur"],
        name="Individus utilisant Internet (% pop - ITU/BM)",
        mode="lines+markers",
        line=dict(color=COLORS["bleu"] if not is_dark else "#60A5FA", width=3),
        marker=dict(size=7, color=COLORS["bleu"] if not is_dark else "#60A5FA"),
        hovertemplate="<b>Année %{x}</b><br>Utilisateurs Internet : <b>%{y:.1f}%</b> de la pop.<extra></extra>"
    ))
    
    # Série ARCEP (Taux de pénétration)
    fig.add_trace(go.Scatter(
        x=pen_df["annee"],
        y=pen_df["valeur"],
        name="Taux de pénétration abonnements (ARCEP)",
        mode="lines+markers",
        line=dict(color=COLORS["vert"] if not is_dark else "#22C55E", width=2, dash="dash"),
        marker=dict(size=6, color=COLORS["vert"] if not is_dark else "#22C55E"),
        hovertemplate="<b>Année %{x}</b><br>Taux de pénétration ARCEP : <b>%{y:.1f}%</b><extra></extra>"
    ))
    
    # Annotations contextuelles d'accélération
    fig.add_annotation(
        x=2018, y=15.5,
        text="Lancement commercial 4G (2018)",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#9CA3AF" if is_dark else COLORS["text_secondary"],
        ax=-40, ay=-40,
        font=dict(size=11, color="#F3F4F6" if is_dark else COLORS["text_primary"]),
        bgcolor="rgba(30,41,59,0.9)" if is_dark else "rgba(255,255,255,0.9)",
        bordercolor="#475569" if is_dark else COLORS["border"],
        borderwidth=1
    )
    fig.add_annotation(
        x=2022, y=37.6,
        text="37.6% (Record 2022)",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLORS["bleu"] if not is_dark else "#60A5FA",
        ax=-50, ay=-25,
        font=dict(size=11, color="#60A5FA" if is_dark else COLORS["bleu"], weight="bold"),
        bgcolor="rgba(30,41,59,0.9)" if is_dark else "rgba(255,255,255,0.9)",
        bordercolor="#2563EB" if is_dark else COLORS["bleu_border"],
        borderwidth=1
    )
    
    # Pas de titre interne qui chevauche la légende
    apply_plotly_theme(fig, height=400, show_legend=True, is_dark=is_dark)
    fig.update_yaxes(title_text="Pourcentage (%)", range=[0, 55])
    fig.update_xaxes(title_text="Année", dtick=2)
    
    return fig

def layout():
    kpis = get_overview_kpis()
    
    return html.Div(
        className="main-container",
        children=[
            # En-tête de la page
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("SYNTHÈSE EXÉCUTIVE", className="page-question-tag bleu"),
                    html.H2("L'inclusion numérique au Togo en un regard", className="page-title"),
                    html.P(
                        "Vision consolidée de la pénétration d'Internet, de l'infrastructure télécoms et du "
                        "déploiement des points d'accès financiers physiques et mobiles sur le territoire togolais.",
                        className="page-description"
                    )
                ]
            ),
            
            # Les 4 KPI obligatoires
            html.Div(
                className="grid-4",
                children=[
                    create_kpi_card(
                        label=kpis["internet_penetration"]["label"],
                        value=kpis["internet_penetration"]["valeur"],
                        period=kpis["internet_penetration"]["periode"],
                        interpretation=kpis["internet_penetration"]["interpretation"],
                        domain=kpis["internet_penetration"]["domaine"]
                    ),
                    create_kpi_card(
                        label=kpis["internet_subscribers"]["label"],
                        value=kpis["internet_subscribers"]["valeur"],
                        period=kpis["internet_subscribers"]["periode"],
                        interpretation=kpis["internet_subscribers"]["interpretation"],
                        domain=kpis["internet_subscribers"]["domaine"]
                    ),
                    create_kpi_card(
                        label=kpis["mm_agents"]["label"],
                        value=kpis["mm_agents"]["valeur"],
                        period=kpis["mm_agents"]["periode"],
                        interpretation=kpis["mm_agents"]["interpretation"],
                        domain=kpis["mm_agents"]["domaine"]
                    ),
                    create_kpi_card(
                        label=kpis["financial_points"]["label"],
                        value=kpis["financial_points"]["valeur"],
                        period=kpis["financial_points"]["periode"],
                        interpretation=kpis["financial_points"]["interpretation"],
                        domain=kpis["financial_points"]["domaine"]
                    )
                ]
            ),
            
            # Section centrale : Graphique + Observations À Retenir
            html.Div(
                className="grid-2-1",
                children=[
                    # Graphique d'évolution
                    create_chart_box(
                        question="QUESTION : QUELLE EST LA DYNAMIQUE GLOBALE D'ADOPTION DU NUMÉRIQUE ?",
                        title="Évolution temporelle de l'accès à Internet au Togo (2005 – 2022)",
                        chart_component=dcc.Graph(id="overview-trend-graph", config={"displayModeBar": False}),
                        source="Banque Mondiale (WDI 2023) & ARCEP Togo (Rapports 2013-2019)",
                        subtitle="Comparaison des mesures d'utilisation individuelle (ITU/BM) et de pénétration des abonnements (ARCEP)"
                    ),
                    
                    # Bloc "À RETENIR"
                    html.Div(
                        className="card-box",
                        children=[
                            html.Div(className="card-header", children=[
                                html.Div("SYNTHÈSE ANALYTIQUE", className="card-question"),
                                html.H3("À retenir des données", className="card-title"),
                                html.P("Observations vérifiables dérivées des séries consolidées", className="card-subtitle")
                            ]),
                            html.Div([
                                html.Div(className="observation-box", children=[
                                    html.Div("1. Accélération de l'accès individuel", className="observation-title"),
                                    html.P("Le taux d'utilisation d'Internet est passé de 4.5% en 2013 à 37.6% en 2022. Près de 4 Togolais sur 10 utilisent désormais Internet.")
                                ]),
                                html.Div(className="observation-box", children=[
                                    html.Div("2. Le Mobile Money, premier vecteur d'inclusion", className="observation-title"),
                                    html.P("Avec 19 788 agents recensés contre seulement 738 agences financières physiques (banques/microfinances), le Mobile Money offre un maillage 27 fois plus dense.")
                                ]),
                                html.Div(className="observation-box", children=[
                                    html.Div("3. Polarisation géographique côtière", className="observation-title"),
                                    html.P("La région Maritime et le Grand Lomé concentrent 56% des établissements financiers et 45% des agents Mobile Money, révélant une fracture Nord-Sud persistante.")
                                ])
                            ])
                        ]
                    )
                ]
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        Output("overview-trend-graph", "figure"),
        Input("theme-store", "data")
    )
    def update_overview_theme(theme_data):
        is_dark = (theme_data == "dark")
        return create_overview_chart(is_dark=is_dark)
