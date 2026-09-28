"""
pages/internet.py
=================
Page 2 : Analyse approfondie de l'évolution de l'utilisation d'Internet au Togo.
Question : Comment l'utilisation d'Internet évolue-t-elle au Togo ?
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from utils.data_loader import get_internet_users, get_internet_tech
from utils.theme import COLORS, apply_plotly_theme
from components.chart_container import create_chart_box

def get_internet_series_options():
    return [
        {"label": "Part de la population utilisant Internet (% - ITU / Banque Mondiale)", "value": "itu_users"},
        {"label": "Taux de pénétration Internet toutes technologies (% - ARCEP)", "value": "arcep_penetration"},
        {"label": "Nombre total d'abonnés Internet Fixe et Mobile (ARCEP)", "value": "arcep_subscribers"},
        {"label": "Taux de pénétration Internet haut débit (% - ARCEP)", "value": "arcep_broadband"},
    ]

def layout():
    return html.Div(
        className="main-container",
        children=[
            # En-tête
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("QUESTION ANALYTIQUE 1", className="page-question-tag bleu"),
                    html.H2("Comment l'utilisation d'Internet évolue-t-elle au Togo ?", className="page-title"),
                    html.P(
                        "Analyse de la trajectoire historique de pénétration et comparaison des métriques d'usage individuel "
                        "face aux parcs d'abonnements déclarés par les opérateurs de télécommunications.",
                        className="page-description"
                    )
                ]
            ),
            
            # Panneau de contrôle / sélecteur
            html.Div(
                className="control-panel",
                children=[
                    html.Div([
                        html.Label("Sélectionner l'indicateur d'analyse :", className="control-label"),
                        dcc.Dropdown(
                            id="internet-indicator-selector",
                            options=get_internet_series_options(),
                            value="itu_users",
                            clearable=False,
                            style={"width": "460px", "fontSize": "13px"}
                        )
                    ]),
                    html.Div([
                        html.Label("Plage temporelle :", className="control-label"),
                        dcc.RadioItems(
                            id="internet-period-selector",
                            options=[
                                {"label": "Cycle récent (2010 – 2022)", "value": "recent"},
                                {"label": "Historique complet (depuis 1995)", "value": "all"}
                            ],
                            value="recent",
                            inline=True,
                            style={"fontSize": "13px", "display": "flex", "gap": "16px"}
                        )
                    ])
                ]
            ),
            
            # Bandeau de métriques dynamiques
            html.Div(id="internet-dynamic-kpi-row", className="grid-4"),
            
            # Graphique principal grand format
            create_chart_box(
                question="TRAJECTOIRE TEMPORELLE ET VARIATION ANNUELLE",
                title="Évolution de la métrique d'utilisation d'Internet",
                chart_component=dcc.Graph(id="internet-main-graph", config={"displayModeBar": False}),
                source="ARCEP Togo & Union Internationale des Télécommunications (UIT) / Banque Mondiale",
                subtitle="Sélectionnez l'indicateur ci-dessus pour observer les variations de pente et les points d'inflexion."
            ),
            
            # Note méthodologique comparative obligatoire
            html.Div(
                className="card-box",
                style={"marginTop": "20px"},
                children=[
                    html.Div(className="card-header", children=[
                        html.Div("NOTE MÉTHODOLOGIQUE MAJEURE", className="card-question"),
                        html.H3("Ne pas confondre 'Taux d'utilisation' et 'Taux de pénétration des abonnements'", className="card-title")
                    ]),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "24px", "fontSize": "13px", "color": "#4B5563"},
                        children=[
                            html.Div([
                                html.H4("Individus utilisant Internet (% de la population)", style={"color": "#111827", "fontWeight": "600", "marginBottom": "6px"}),
                                html.P(
                                    "Mesure issue des enquêtes ménages et rapports officiels ITU/Banque Mondiale. "
                                    "Elle comptabilise les individus uniques ayant utilisé Internet au cours des 3 derniers mois, "
                                    "quel que soit le terminal ou le mode d'accès (personnel, cybercafé, smartphone d'un proche). "
                                    "Valeur 2022 : 37.6%."
                                )
                            ]),
                            html.Div([
                                html.H4("Taux de pénétration des abonnements (ARCEP)", style={"color": "#111827", "fontWeight": "600", "marginBottom": "6px"}),
                                html.P(
                                    "Rapport brut entre le nombre total de cartes SIM/lignes Internet actives déclarées "
                                    "par les opérateurs et la population totale. En raison du multi-équipement (multi-SIM), "
                                    "ce chiffre dépasse souvent le pourcentage de personnes physiques connectées. "
                                    "Valeur 2019 : 44.8% pour 3.41 millions d'abonnements."
                                )
                            ])
                        ]
                    )
                ]
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        [Output("internet-main-graph", "figure"),
         Output("internet-dynamic-kpi-row", "children")],
        [Input("internet-indicator-selector", "value"),
         Input("internet-period-selector", "value"),
         Input("theme-store", "data")]
    )
    def update_internet_chart(selected_indicator, period_range, theme_data):
        is_dark = (theme_data == "dark")
        users_df = get_internet_users()
        tech_df = get_internet_tech()
        
        fig = go.Figure()
        
        if selected_indicator == "itu_users":
            df = users_df.dropna(subset=["valeur"]).copy()
            if period_range == "recent":
                df = df[df["annee"] >= 2010]
            else:
                df = df[df["annee"] >= 1995]
            df = df.sort_values("annee")
            
            fig.add_trace(go.Scatter(
                x=df["annee"],
                y=df["valeur"],
                mode="lines+markers",
                name="Utilisateurs Internet (%)",
                line=dict(color=COLORS["bleu"] if not is_dark else "#60A5FA", width=3),
                marker=dict(size=7, color=COLORS["bleu"] if not is_dark else "#60A5FA"),
                hovertemplate="<b>%{x}</b> : %{y:.2f}% de la population<extra></extra>"
            ))
            unit_str = "%"
            current_val = f"{df['valeur'].iloc[-1]:.1f}%"
            last_year = int(df['annee'].iloc[-1])
            prev_val = df['valeur'].iloc[-2] if len(df) > 1 else df['valeur'].iloc[-1]
            variation = f"+{(df['valeur'].iloc[-1] - prev_val):.1f} pts"
            
        elif selected_indicator == "arcep_penetration":
            df = tech_df[tech_df["indicateur"].str.contains("Toutes technologies", na=False)].sort_values("annee")
            fig.add_trace(go.Scatter(
                x=df["annee"],
                y=df["valeur"],
                mode="lines+markers",
                name="Pénétration globale ARCEP (%)",
                line=dict(color=COLORS["vert"] if not is_dark else "#22C55E", width=3),
                marker=dict(size=7, color=COLORS["vert"] if not is_dark else "#22C55E"),
                hovertemplate="<b>%{x}</b> : %{y:.2f}% de pénétration<extra></extra>"
            ))
            unit_str = "%"
            current_val = f"{df['valeur'].iloc[-1]:.1f}%"
            last_year = int(df['annee'].iloc[-1])
            variation = f"+{(df['valeur'].iloc[-1] - df['valeur'].iloc[0]):.1f} pts"
            
        elif selected_indicator == "arcep_subscribers":
            df = tech_df[tech_df["indicateur"].str.contains("Fixe et Mobile", na=False)].sort_values("annee")
            fig.add_trace(go.Bar(
                x=df["annee"],
                y=df["valeur"],
                name="Abonnements Internet",
                marker_color=COLORS["bleu"] if not is_dark else "#3B82F6",
                hovertemplate="<b>%{x}</b> : %{y:,.0f} abonnés<extra></extra>"
            ))
            unit_str = "abonnés"
            current_val = f"{df['valeur'].iloc[-1]:,.0f}".replace(",", " ")
            last_year = int(df['annee'].iloc[-1])
            growth_factor = df['valeur'].iloc[-1] / df['valeur'].iloc[0]
            variation = f"x{growth_factor:.1f} depuis {int(df['annee'].iloc[0])}"
            
        else: # arcep_broadband
            df = tech_df[tech_df["indicateur"].str.contains("haut débit", na=False) & tech_df["indicateur"].str.contains("Taux", na=False)].sort_values("annee")
            fig.add_trace(go.Scatter(
                x=df["annee"],
                y=df["valeur"],
                mode="lines+markers",
                name="Pénétration haut débit (%)",
                line=dict(color=COLORS["violet"] if not is_dark else "#A78BFA", width=3),
                marker=dict(size=7, color=COLORS["violet"] if not is_dark else "#A78BFA"),
                hovertemplate="<b>%{x}</b> : %{y:.2f}%<extra></extra>"
            ))
            unit_str = "%"
            current_val = f"{df['valeur'].iloc[-1]:.1f}%"
            last_year = int(df['annee'].iloc[-1])
            variation = f"+{(df['valeur'].iloc[-1] - df['valeur'].iloc[0]):.1f} pts"

        # Pas de titre interne qui chevauche la légende
        apply_plotly_theme(fig, height=420, show_legend=True, is_dark=is_dark)
        fig.update_xaxes(dtick=1 if period_range == "recent" else 2)

        # Cartes métriques dynamiques
        cards = [
            html.Div(className="kpi-card bleu", children=[
                html.Div("Dernière valeur observée", className="kpi-label"),
                html.Div(current_val, className="kpi-value"),
                html.Div(f"Année de référence : {last_year}", className="kpi-periode")
            ]),
            html.Div(className="kpi-card vert", children=[
                html.Div("Variation constatée", className="kpi-label"),
                html.Div(variation, className="kpi-value", style={"fontSize": "22px"}),
                html.Div("Dynamique positive continue", className="kpi-periode")
            ]),
            html.Div(className="kpi-card violet", children=[
                html.Div("Unité de mesure", className="kpi-label"),
                html.Div(unit_str, className="kpi-value", style={"fontSize": "22px"}),
                html.Div("Format statistique certifié", className="kpi-periode")
            ]),
            html.Div(className="kpi-card jaune", children=[
                html.Div("Statut de la donnée", className="kpi-label"),
                html.Div("Consolidé", className="kpi-value", style={"fontSize": "22px"}),
                html.Div("Source institutionnelle", className="kpi-periode")
            ]),
        ]

        return fig, cards
