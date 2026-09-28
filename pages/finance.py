"""
pages/finance.py
================
Page 5 : Accessibilité des services financiers et du Mobile Money sur le territoire.
Question : Dans quelle mesure les services financiers sont-ils accessibles sur le territoire ?
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import get_finance_clean, get_mobile_money_clean
from utils.calculations import get_consolidated_regions_data, get_prefectures_summary
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
                    html.Span("QUESTION ANALYTIQUE 4", className="page-question-tag violet"),
                    html.H2("Dans quelle mesure les services financiers sont-ils accessibles sur le territoire ?", className="page-title"),
                    html.P(
                        "Examen des réseaux de distribution bancaire traditionnelle, de la microfinance et de l'infrastructure "
                        "Mobile Money. Distinction stricte entre volume brut d'implantations et densité relative par habitant.",
                        className="page-description"
                    )
                ]
            ),
            
            # Contrôles de filtre
            html.Div(
                className="control-panel",
                children=[
                    html.Div([
                        html.Label("Catégorie financière à analyser :", className="control-label"),
                        dcc.Dropdown(
                            id="finance-category-selector",
                            options=[
                                {"label": "Toutes catégories financières (Vue consolidée)", "value": "ALL"},
                                {"label": "Micro-Finance (413 agences - inclusion de proximité)", "value": "Micro-Finance"},
                                {"label": "Banques commerciales (247 agences)", "value": "Banque"},
                                {"label": "Compagnies d'assurance (69 implantations)", "value": "Assurance"},
                                {"label": "Mutuelles de santé / épargne (9 entités)", "value": "Mutuelle"}
                            ],
                            value="ALL",
                            clearable=False,
                            style={"width": "460px", "fontSize": "13px"}
                        )
                    ]),
                    html.Div([
                        html.Label("Métrique d'évaluation :", className="control-label"),
                        dcc.RadioItems(
                            id="finance-metric-selector",
                            options=[
                                {"label": "Accessibilité relative (Points pour 10 000 hab)", "value": "relative"},
                                {"label": "Volume brut (Nombre absolu d'agences)", "value": "absolute"}
                            ],
                            value="relative",
                            inline=True,
                            style={"fontSize": "13px", "display": "flex", "gap": "16px"}
                        )
                    ])
                ]
            ),
            
            # Graphiques
            html.Div(
                className="grid-2",
                children=[
                    create_chart_box(
                        question="RÉPARTITION PAR RÉGION",
                        title="Distribution des services financiers sélectionnés",
                        chart_component=dcc.Graph(id="finance-region-chart", config={"displayModeBar": False}),
                        source="Répertoire des établissements financiers (Janvier 2025) & INSEED (2022)"
                    ),
                    create_chart_box(
                        question="COMPARAISON DES VECTEURS D'INCLUSION",
                        title="Mobile Money vs Agences physiques : le facteur multiplicateur",
                        chart_component=dcc.Graph(id="finance-comparison-chart", config={"displayModeBar": False}),
                        source="Cartographie Mobile Money (2024) & Répertoire Financier (2025)",
                        subtitle="Mise en lumière du rôle de désenclavement joué par les agents mobiles dans l'intérieur du pays."
                    )
                ]
            ),
            
            # Zoom Préfectures : Top 10 des préfectures
            html.Div(
                className="card-box",
                children=[
                    html.Div(className="card-header", children=[
                        html.Div("DISPARITÉS INFRA-RÉGIONALES", className="card-question"),
                        html.H3("Top 10 des préfectures togolaises par concentration de services financiers", className="card-title"),
                        html.P("Les données mettent en évidence la macrocéphalie de la préfecture du Golfe (Grand Lomé) face aux préfectures de l'intérieur.", className="card-subtitle")
                    ]),
                    html.Div(id="finance-prefectures-table")
                ]
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        [Output("finance-region-chart", "figure"),
         Output("finance-comparison-chart", "figure"),
         Output("finance-prefectures-table", "children")],
        [Input("finance-category-selector", "value"),
         Input("finance-metric-selector", "value"),
         Input("theme-store", "data")]
    )
    def update_finance_view(cat_filter, metric_mode, theme_data):
        is_dark = (theme_data == "dark")
        fin_df = get_finance_clean()
        df_reg = get_consolidated_regions_data().copy()
        
        # Filtrage catégorie
        if cat_filter != "ALL":
            sub_fin = fin_df[fin_df["activite_categorie"] == cat_filter]
            counts = sub_fin.groupby("region_normalisee").size().to_dict()
        else:
            counts = fin_df.groupby("region_normalisee").size().to_dict()
            
        regions = ["SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME"]
        labels = ["Savanes", "Kara", "Centrale", "Plateaux", "Maritime"]
        raw_vals = [counts.get(r, 0) for r in regions]
        
        pop_map = dict(zip(df_reg["region"], df_reg["population"]))
        rel_vals = [round((raw_vals[i] / pop_map[regions[i]]) * 10000, 2) for i in range(5)]
        
        # 1. Graphique régional mono-série (PAS DE LÉGENDE 'trace 0', PAS DE TITRE REDONDANT)
        fig_reg = go.Figure()
        if metric_mode == "relative":
            fig_reg.add_trace(go.Bar(
                x=labels, y=rel_vals,
                marker_color=COLORS["vert"] if not is_dark else "#22C55E",
                showlegend=False,
                hovertemplate="<b>%{x}</b> : %{y:.2f} pour 10 000 hab.<extra></extra>"
            ))
            y_title = "Points pour 10 000 habitants"
        else:
            fig_reg.add_trace(go.Bar(
                x=labels, y=raw_vals,
                marker_color=COLORS["bleu"] if not is_dark else "#60A5FA",
                showlegend=False,
                hovertemplate="<b>%{x}</b> : %{y:,.0f} agences physiques<extra></extra>"
            ))
            y_title = "Nombre absolu d'agences"
            
        apply_plotly_theme(fig_reg, height=340, show_legend=False, is_dark=is_dark)
        fig_reg.update_yaxes(title_text=y_title)
        
        # 2. Graphique comparatif Mobile Money vs Finance physique
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Agents Mobile Money (proximité)",
            x=labels,
            y=df_reg["agents_pour_10000_hab"],
            marker_color=COLORS["violet"] if not is_dark else "#A78BFA",
            hovertemplate="<b>%{x}</b> (MM) : %{y:.1f} / 10k hab.<extra></extra>"
        ))
        fig_comp.add_trace(go.Bar(
            name="Agences financières classiques",
            x=labels,
            y=df_reg["etab_pour_10000_hab"],
            marker_color=COLORS["vert"] if not is_dark else "#22C55E",
            hovertemplate="<b>%{x}</b> (Banques) : %{y:.2f} / 10k hab.<extra></extra>"
        ))
        # Pas de titre qui écrase la légende
        apply_plotly_theme(fig_comp, height=340, show_legend=True, is_dark=is_dark)
        fig_comp.update_layout(barmode="group")
        fig_comp.update_yaxes(title_text="Points de service / 10 000 hab")
        
        # 3. Tableau préfectoral Top 10
        pref_df = get_prefectures_summary().head(10)
        table_rows = []
        for _, p in pref_df.iterrows():
            table_rows.append(html.Tr([
                html.Td(html.B(p["prefecture"].title())),
                html.Td(p["region"].title()),
                html.Td(f"{p['nb_agents']:,.0f}".replace(",", " ")),
                html.Td(f"{p['nb_etablissements']:,.0f}".replace(",", " ")),
                html.Td(f"{(p['nb_agents'] / max(1, p['nb_etablissements'])):.1f}x plus d'agents MM")
            ]))
            
        pref_table = html.Table(
            className="data-table-simple",
            children=[
                html.Thead(html.Tr([
                    html.Th("Préfecture"),
                    html.Th("Région de rattachement"),
                    html.Th("Agents Mobile Money"),
                    html.Th("Agences Financières"),
                    html.Th("Multiplicateur de couverture Mobile Money")
                ])),
                html.Tbody(table_rows)
            ]
        )
        
        return fig_reg, fig_comp, pref_table
