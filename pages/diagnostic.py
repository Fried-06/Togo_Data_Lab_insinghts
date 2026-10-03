"""
pages/diagnostic.py
===================
Page 6 : Diagnostic territorial des déficits d'accès.
Question : Où se trouvent les principaux déficits ?
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from utils.calculations import get_consolidated_regions_data
from utils.theme import COLORS, apply_plotly_theme
from components.chart_container import create_chart_box

def layout():
    return html.Div(
        className="main-container",
        children=[
            # En-tête
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("CŒUR ANALYTIQUE", className="page-question-tag rouge"),
                    html.H2("Où se trouvent les principaux déficits ?", className="page-title"),
                    html.P(
                        "Évaluation objective des disparités régionales fondée sur les écarts relatifs à la moyenne "
                        "nationale pondérée. Identification rigoureuse des zones sous-desservies.",
                        className="page-description"
                    )
                ]
            ),
            
            # Sélecteur de domaine d'analyse
            html.Div(
                className="control-panel",
                children=[
                    html.Div([
                        html.Label("Domaine d'analyse diagnostique :", className="control-label"),
                        dcc.Dropdown(
                            id="diagnostic-domain-selector",
                            options=[
                                {"label": "Services financiers physiques (Banques, Microfinances)", "value": "finance"},
                                {"label": "Réseau Mobile Money (Agents de proximité)", "value": "mobile_money"},
                                {"label": "Indice composite d'inclusion financière", "value": "composite"}
                            ],
                            value="composite",
                            clearable=False,
                            style={"width": "460px", "fontSize": "13px"}
                        )
                    ])
                ]
            ),
            
            # Graphique d'écart à la moyenne nationale
            create_chart_box(
                question="DISPARITÉS RELATIVES FACE À LA NORME NATIONALE",
                title="Écart en pourcentage (%) à la moyenne nationale pondérée",
                chart_component=dcc.Graph(id="diagnostic-gap-chart", config={"displayModeBar": False}),
                source="Calculs Togo Digital Insight - Donnees certifiees RGPH-5 (2022) et Releves de terrain (2024-2025)",
                subtitle="La ligne centrale (0%) représente la moyenne nationale togolaise. Les barres à gauche indiquent un sous-équipement relatif."
            ),
            
            # Matrice de synthèse diagnostique & Méthodologie
            html.Div(
                className="grid-2-1",
                children=[
                    # Tableau diagnostique
                    html.Div(
                        className="card-box",
                        children=[
                            html.Div(className="card-header", children=[
                                html.Div("SYNTHÈSE PAR TERRITOIRE", className="card-question"),
                                html.H3("Matrice de qualification territoriale", className="card-title")
                            ]),
                            html.Div(id="diagnostic-matrix-table")
                        ]
                    ),
                    
                    # Encadré Méthodologie
                    html.Div(
                        className="card-box",
                        children=[
                            html.Div(className="card-header", children=[
                                html.Div("TRANSPARENCE STATISTIQUE", className="card-question"),
                                html.H3("Méthodologie de catégorisation", className="card-title")
                            ]),
                            html.Div(style={"fontSize": "13px", "color": "var(--text-secondary)", "lineHeight": "1.6"}, children=[
                                html.P(
                                    "Pour éviter tout jugement de valeur arbitraire, la qualification repose strictement sur l'écart relatif (Δ) "
                                    "par rapport au ratio moyen national pondéré :",
                                    style={"marginBottom": "10px"}
                                ),
                                html.Div(style={"marginBottom": "8px"}, children=[
                                    html.Span("Favorable", className="status-pill favorable"),
                                    html.Span(" : Ratio supérieur de plus de +15% à la moyenne nationale. Écosystème dense et diversifié.", style={"fontSize": "12px", "marginLeft": "8px"})
                                ]),
                                html.Div(style={"marginBottom": "8px"}, children=[
                                    html.Span("Intermédiaire", className="status-pill intermediaire"),
                                    html.Span(" : Ratio situé entre -20% et +15% de la moyenne. Couverture fonctionnelle mais perfectible.", style={"fontSize": "12px", "marginLeft": "8px"})
                                ]),
                                html.Div(style={"marginBottom": "12px"}, children=[
                                    html.Span("Déficit", className="status-pill deficit"),
                                    html.Span(" : Ratio inférieur de plus de -20% à la moyenne. Sous-densité critique nécessitant un appui ciblé.", style={"fontSize": "12px", "marginLeft": "8px"})
                                ]),
                                html.P(
                                    "Note : La région des Savanes et la région des Plateaux présentent des déficits structurels marqués en agences physiques, "
                                    "partiellement compensés par les réseaux de Mobile Money.",
                                    style={"borderTop": "1px solid var(--border)", "paddingTop": "10px", "fontStyle": "italic"}
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
        [Output("diagnostic-gap-chart", "figure"),
         Output("diagnostic-matrix-table", "children")],
        [Input("diagnostic-domain-selector", "value"),
         Input("theme-store", "data")]
    )
    def update_diagnostic(domain, theme_data):
        is_dark = (theme_data == "dark")
        df_reg = get_consolidated_regions_data().copy()
        
        if domain == "finance":
            col_gap = "ecart_etab_pct"
            bar_color_pos = COLORS["vert"] if not is_dark else "#22C55E"
            bar_color_neg = COLORS["rouge"] if not is_dark else "#EF4444"
        elif domain == "mobile_money":
            col_gap = "ecart_agents_pct"
            bar_color_pos = COLORS["violet"] if not is_dark else "#A78BFA"
            bar_color_neg = COLORS["rouge"] if not is_dark else "#EF4444"
        else: # composite
            df_reg["composite_gap"] = ((df_reg["ecart_agents_pct"] + df_reg["ecart_etab_pct"]) / 2).round(1)
            col_gap = "composite_gap"
            bar_color_pos = COLORS["vert"] if not is_dark else "#22C55E"
            bar_color_neg = COLORS["rouge"] if not is_dark else "#EF4444"
            
        # Tri pour affichage clair
        df_sorted = df_reg.sort_values(by=col_gap, ascending=True)
        
        # Graphique des écarts
        colors = [bar_color_pos if x >= 0 else bar_color_neg for x in df_sorted[col_gap]]
        
        fig = go.Figure(go.Bar(
            y=df_sorted["region_label"],
            x=df_sorted[col_gap],
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.1f}%" for v in df_sorted[col_gap]],
            textposition="outside",
            hovertemplate="<b>%{y}</b> : Écart de <b>%{x:+.1f}%</b><extra></extra>"
        ))
        
        fig.add_vline(x=0, line_color="#475569" if is_dark else "#374151", line_width=1.5)
        # Pas de titre interne qui chevauche la légende ou les barres
        apply_plotly_theme(fig, height=320, show_legend=False, is_dark=is_dark)
        fig.update_xaxes(title_text="Écart à la moyenne nationale (%)", zeroline=True)
        fig.update_yaxes(title_text="")
        
        # Tableau diagnostique
        rows = []
        for _, r in df_sorted.iterrows():
            gap_val = r[col_gap]
            status = "Favorable" if gap_val > 15 else ("Intermédiaire" if gap_val >= -20 else "Déficit")
            status_cls = "favorable" if status == "Favorable" else ("intermediaire" if status == "Intermédiaire" else "deficit")
            
            rows.append(html.Tr([
                html.Td(html.B(r["region_label"])),
                html.Td(f"{r['population']:,.0f}".replace(",", " ")),
                html.Td(f"{gap_val:+.1f}%"),
                html.Td(html.Span(status, className=f"status-pill {status_cls}"))
            ]))
            
        table = html.Table(
            className="data-table-simple",
            children=[
                html.Thead(html.Tr([
                    html.Th("Région"),
                    html.Th("Population 2022"),
                    html.Th("Écart relatif"),
                    html.Th("Niveau de qualification")
                ])),
                html.Tbody(rows)
            ]
        )
        
        return fig, table
