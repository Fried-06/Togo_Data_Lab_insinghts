"""
pages/connectivity.py
=====================
Page 3 : Analyse des technologies d'accès à Internet et de la transition technologique.
Question : Comment les Togolais accèdent-ils à Internet ?
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import get_internet_tech, get_telecom
from utils.theme import COLORS, apply_plotly_theme
from components.chart_container import create_chart_box

def create_tech_transition_chart(is_dark=False):
    """Génère la stacked bar chart montrant la bascule technologique 2G -> 3G -> 4G."""
    df = get_internet_tech()
    years = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
    
    # 2G (GPRS / EDGE)
    gprs_tc = df[df["indicateur"].str.contains("GPRS /EDGE Togo Cellulaire", na=False)].set_index("annee")["valeur"]
    gprs_at = df[df["indicateur"].str.contains("GPRS/EDGE Atlantique Telecom", na=False)].set_index("annee")["valeur"]
    total_2g = [float(gprs_tc.get(y, 0) + gprs_at.get(y, 0)) for y in years]
    
    # 3G
    c3g_tc = df[df["indicateur"].str.contains("clients 3G Togo Cellulaire", na=False)].set_index("annee")["valeur"]
    c3g_at = df[df["indicateur"].str.contains("clients 3G Atlantique Telecom", na=False)].set_index("annee")["valeur"]
    total_3g = [float(c3g_tc.get(y, 0) + c3g_at.get(y, 0)) for y in years]
    
    # 4G
    c4g_tc = df[df["indicateur"].str.contains("clients 4G Togo Cellulaire", na=False)].set_index("annee")["valeur"]
    c4g_at = df[df["indicateur"].str.contains("clients 4G Atlantique Telecom", na=False)].set_index("annee")["valeur"]
    total_4g = [float(c4g_tc.get(y, 0) + c4g_at.get(y, 0)) for y in years]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years, y=total_2g,
        name="2G (GPRS / EDGE)",
        marker_color="#9CA3AF" if not is_dark else "#64748B",
        hovertemplate="<b>2G</b> (%{x}) : %{y:,.0f} clients<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=years, y=total_3g,
        name="3G (Haut débit mobile)",
        marker_color=COLORS["bleu"],
        hovertemplate="<b>3G</b> (%{x}) : %{y:,.0f} clients<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=years, y=total_4g,
        name="4G (Très haut débit mobile)",
        marker_color=COLORS["vert"] if not is_dark else "#22C55E",
        hovertemplate="<b>4G</b> (%{x}) : %{y:,.0f} clients<extra></extra>"
    ))
    
    fig.update_layout(barmode="stack")
    # Pas de titre interne qui chevauche la légende !
    apply_plotly_theme(fig, height=380, show_legend=True, is_dark=is_dark)
    fig.update_yaxes(title_text="Nombre d'abonnés")
    return fig

def create_fixed_tech_chart(is_dark=False):
    """Génère la comparaison des technologies fixes (ADSL, FTTH, Wimax, etc.)."""
    df = get_internet_tech()
    years = [2016, 2017, 2018, 2019]
    
    adsl = df[df["indicateur"] == "ADSL"].set_index("annee")["valeur"]
    ftth = df[df["indicateur"] == "FTTH"].set_index("annee")["valeur"]
    wimax = df[df["indicateur"] == "Wimax"].set_index("annee")["valeur"]
    gva = df[df["indicateur"] == "GVA"].set_index("annee")["valeur"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=[adsl.get(y, 0) for y in years],
        name="ADSL (Cuivre)", mode="lines+markers",
        line=dict(color="#B45309" if not is_dark else "#F59E0B", width=2.5),
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[ftth.get(y, 0) for y in years],
        name="FTTH (Fibre à domicile)", mode="lines+markers",
        line=dict(color=COLORS["vert"] if not is_dark else "#22C55E", width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[gva.get(y, 0) for y in years],
        name="GVA (Canalbox)", mode="lines+markers",
        line=dict(color=COLORS["bleu"] if not is_dark else "#60A5FA", width=2.5, dash="dash"),
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[wimax.get(y, 0) for y in years],
        name="Wimax (Hertzien)", mode="lines+markers",
        line=dict(color="#9CA3AF" if not is_dark else "#64748B", width=2),
        marker=dict(size=6)
    ))
    
    # Pas de titre interne qui chevauche la légende !
    apply_plotly_theme(fig, height=380, show_legend=True, is_dark=is_dark)
    fig.update_yaxes(title_text="Lignes actives")
    return fig

def create_operator_share_chart(is_dark=False):
    """Parts de marché des deux opérateurs GSM (Togo Cellulaire vs Moov / Atlantique Telecom)."""
    tel_df = get_telecom()
    pm_tc = tel_df[tel_df["indicateur"].str.contains("Togo Cellulaire", na=False) & tel_df["indicateur"].str.contains("Part", na=False)].sort_values("annee")
    pm_at = tel_df[tel_df["indicateur"].str.contains("Atlantique", na=False) & tel_df["indicateur"].str.contains("Part", na=False)].sort_values("annee")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pm_tc["annee"], y=pm_tc["valeur"],
        name="Togo Cellulaire (Togocom)", mode="lines+markers",
        line=dict(color="#006A4E" if not is_dark else "#22C55E", width=3),
        marker=dict(size=8),
        hovertemplate="Togocom (%{x}) : <b>%{y:.1f}%</b><extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=pm_at["annee"], y=pm_at["valeur"],
        name="Atlantique Telecom (Moov Africa)", mode="lines+markers",
        line=dict(color="#F97316" if not is_dark else "#FB923C", width=3),
        marker=dict(size=8),
        hovertemplate="Moov (%{x}) : <b>%{y:.1f}%</b><extra></extra>"
    ))
    
    fig.add_hline(
        y=50, line_dash="dot",
        line_color="#475569" if is_dark else "#D1D5DB",
        annotation_text="Équilibre 50%",
        annotation_position="top right",
        annotation_font_color="#9CA3AF" if is_dark else "#6B7280"
    )
    apply_plotly_theme(fig, height=340, show_legend=True, is_dark=is_dark)
    fig.update_yaxes(title_text="Part de marché (%)", range=[35, 65])
    return fig

def layout():
    return html.Div(
        className="main-container",
        children=[
            # En-tête
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("QUESTION ANALYTIQUE 2", className="page-question-tag bleu"),
                    html.H2("Comment les Togolais accèdent-ils à Internet ?", className="page-title"),
                    html.P(
                        "Analyse de la répartition des technologies (3G, 4G, ADSL, FTTH) et du rôle écrasant "
                        "du smartphone comme unique passerelle vers le numérique pour plus de 99% des abonnés.",
                        className="page-description"
                    )
                ]
            ),
            
            # Constat clé
            html.Div(
                className="grid-3",
                children=[
                    html.Div(className="kpi-card bleu", children=[
                        html.Div("Part du Mobile dans les connexions", className="kpi-label"),
                        html.Div("99.1%", className="kpi-value"),
                        html.Div("3.38M abonnés mobiles sur 3.41M total (2019)", className="kpi-interpretation")
                    ]),
                    html.Div(className="kpi-card vert", children=[
                        html.Div("Percée de la 3G (Haut Débit)", className="kpi-label"),
                        html.Div("1.88M", className="kpi-value"),
                        html.Div("Clients 3G actifs en 2019 (Togocom + Moov)", className="kpi-interpretation")
                    ]),
                    html.Div(className="kpi-card violet", children=[
                        html.Div("Croissance Fibre Optique (FTTH)", className="kpi-label"),
                        html.Div("x74.8", className="kpi-value"),
                        html.Div("De 92 abonnés en 2017 à 6 888 en 2019", className="kpi-interpretation")
                    ]),
                ]
            ),
            
            # 2 Graphiques en grille
            html.Div(
                className="grid-2",
                children=[
                    create_chart_box(
                        question="TRANSITION TECHNOLOGIQUE MOBILE",
                        title="Bascule des réseaux mobiles : de la 2G vers la 3G/4G",
                        chart_component=dcc.Graph(id="connectivity-tech-chart", config={"displayModeBar": False}),
                        source="ARCEP Togo — Données déclaratives opérateurs",
                        subtitle="Remplacement progressif de la 2G par la 3G à partir de 2016, puis introduction de la 4G en 2018"
                    ),
                    create_chart_box(
                        question="INTERNET FIXE ET FIBRE OPTIQUE",
                        title="Mutation des technologies d'accès fixe",
                        chart_component=dcc.Graph(id="connectivity-fixed-chart", config={"displayModeBar": False}),
                        source="ARCEP Togo — Données des FAI et opérateurs",
                        subtitle="Le FTTH et les réseaux alternatifs (GVA) prennent le relais de l'ADSL historique"
                    )
                ]
            ),
            
            # Parts de marché des opérateurs
            create_chart_box(
                question="DYNAMIQUE CONCURRENTIELLE DU SECTEUR",
                title="Parts de marché des abonnés GSM au Togo (Togocom vs Moov)",
                chart_component=dcc.Graph(id="connectivity-operator-chart", config={"displayModeBar": False}),
                source="ARCEP Togo — Rapports annuels d'activité 2013-2019",
                subtitle="Un duopole compétitif : bascule en 2018 avec Moov à 55.4%, puis rééquilibrage en 2019 (51.4% Togocom)"
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        [Output("connectivity-tech-chart", "figure"),
         Output("connectivity-fixed-chart", "figure"),
         Output("connectivity-operator-chart", "figure")],
        [Input("theme-store", "data")]
    )
    def update_connectivity_theme(theme_data):
        is_dark = (theme_data == "dark")
        return (
            create_tech_transition_chart(is_dark=is_dark),
            create_fixed_tech_chart(is_dark=is_dark),
            create_operator_share_chart(is_dark=is_dark)
        )
