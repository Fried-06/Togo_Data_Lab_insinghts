"""
pages/territories.py
====================
Page 4 : Analyse cartographique et disparités territoriales d'accès.
Question : Où se trouvent les écarts territoriaux ?
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
from utils.calculations import get_consolidated_regions_data
from utils.data_loader import get_geojson_regions
from utils.theme import COLORS, apply_plotly_theme
from components.chart_container import create_chart_box

INDICATOR_CONFIG = {
    "agents_pour_10000_hab": {
        "label": "Agents Mobile Money pour 10 000 habitants",
        "format": "{:.1f}",
        "unit": "agents / 10k hab",
        "colorscale": [[0, "#F5F3FF"], [0.5, "#8B5CF6"], [1, "#4C1D95"]],
        "description": "Indicateur de proximité immédiate des liquidités et des opérations de transfert."
    },
    "habitants_par_agent": {
        "label": "Nombre d'habitants par agent Mobile Money",
        "format": "{:,.0f}",
        "unit": "hab. / agent",
        "colorscale": [[0, "#059669"], [0.5, "#F59E0B"], [1, "#DC2626"]],
        "description": "Plus ce ratio est bas, meilleure est la couverture en points de services de proximité."
    },
    "etab_pour_10000_hab": {
        "label": "Établissements financiers pour 10 000 habitants",
        "format": "{:.2f}",
        "unit": "établissements / 10k hab",
        "colorscale": [[0, "#EBFBEE"], [0.5, "#40C057"], [1, "#0B6623"]],
        "description": "Densité des agences bancaires, microfinances et assurances physiques."
    },
    "population": {
        "label": "Population résidente totale (RGPH-5, 2022)",
        "format": "{:,.0f}",
        "unit": "habitants",
        "colorscale": [[0, "#EFF6FF"], [0.5, "#3B82F6"], [1, "#1E3A8A"]],
        "description": "Dénominateur démographique officiel issu du recensement général 2022."
    }
}

def layout():
    df_reg = get_consolidated_regions_data()
    region_options = [{"label": r["region_label"], "value": r["region"]} for _, r in df_reg.iterrows()]
    
    return html.Div(
        className="main-container",
        children=[
            # En-tête
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("QUESTION ANALYTIQUE 3", className="page-question-tag vert"),
                    html.H2("Où se trouvent les écarts territoriaux ?", className="page-title"),
                    html.P(
                        "Cartographie interactive des 5 régions togolaises. Comparaison des indicateurs absolus "
                        "et des ratios d'accessibilité relative pour identifier les disparités d'inclusion.",
                        className="page-description"
                    )
                ]
            ),
            
            # Contrôles de la carte
            html.Div(
                className="control-panel",
                children=[
                    html.Div([
                        html.Label("Indicateur cartographique :", className="control-label"),
                        dcc.Dropdown(
                            id="territory-indicator-select",
                            options=[{"label": v["label"], "value": k} for k, v in INDICATOR_CONFIG.items()],
                            value="agents_pour_10000_hab",
                            clearable=False,
                            style={"width": "420px", "fontSize": "13px"}
                        )
                    ]),
                    html.Div([
                        html.Label("Zoomer sur une région :", className="control-label"),
                        dcc.Dropdown(
                            id="territory-region-select",
                            options=[{"label": "Toutes les régions (Vue Nationale)", "value": "ALL"}] + region_options,
                            value="ALL",
                            clearable=False,
                            style={"width": "300px", "fontSize": "13px"}
                        )
                    ])
                ]
            ),
            
            # Grille Carte + Panneau latéral interactif
            html.Div(
                className="grid-2-1",
                children=[
                    # Carte Choropleth
                    create_chart_box(
                        question="CARTOGRAPHIE CHOROPLETHE DES DISPARITÉS RÉGIONALES",
                        title="Répartition spatiale de l'indicateur sélectionné",
                        chart_component=dcc.Graph(
                            id="territory-choropleth-map",
                            config={"displayModeBar": False, "scrollZoom": False},
                            style={"height": "520px"}
                        ),
                        source="INSEED (RGPH-5 2022), Cartographie Mobile Money (2024), Répertoire Financier (2025)",
                        subtitle="Survolez ou cliquez sur une région pour actualiser le profil détaillé à droite."
                    ),
                    
                    # Panneau régional dynamique
                    html.Div(id="territory-detail-panel")
                ]
            ),
            
            # Tableau récapitulatif comparatif
            html.Div(
                className="card-box",
                children=[
                    html.Div(className="card-header", children=[
                        html.Div("BENCHMARK TERRITORIAL COMPLET", className="card-question"),
                        html.H3("Tableau comparatif des 5 régions administratives du Togo", className="card-title"),
                        html.P("Comparaison directe des populations, des volumes de points de service et des densités pour 10 000 habitants.", className="card-subtitle")
                    ]),
                    html.Div(id="territory-benchmark-table")
                ]
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        [Output("territory-choropleth-map", "figure"),
         Output("territory-detail-panel", "children"),
         Output("territory-benchmark-table", "children")],
        [Input("territory-indicator-select", "value"),
         Input("territory-region-select", "value"),
         Input("territory-choropleth-map", "clickData"),
         Input("theme-store", "data")]
    )
    def update_territory_view(indicator_key, dropdown_region, map_click, theme_data):
        is_dark = (theme_data == "dark")
        df_reg = get_consolidated_regions_data().copy()
        geojson = get_geojson_regions()
        cfg = INDICATOR_CONFIG[indicator_key]
        
        # Déterminer la région sélectionnée
        selected_region = dropdown_region
        if map_click and "points" in map_click and len(map_click["points"]) > 0:
            clicked_iso = map_click["points"][0].get("location")
            match_row = df_reg[df_reg["shapeISO"] == clicked_iso]
            if not match_row.empty:
                selected_region = match_row["region"].values[0]
                
        # Construction de la carte Choropleth
        # Utilisation de go.Choroplethmap (API MapLibre/OpenStreetMap) :
        # - Ne requiert aucun token Mapbox
        # - Fonctionne identiquement en local et sur Plotly Cloud
        # - "open-street-map" est résolu côté client, sans appel externe bloquant
        line_color = "#1E293B" if is_dark else "#FFFFFF"
        map_style = "carto-darkmatter" if is_dark else "open-street-map"

        fig = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=df_reg["shapeISO"],
            z=df_reg[indicator_key],
            featureidkey="properties.shapeISO",
            colorscale=cfg["colorscale"],
            text=df_reg["region_label"],
            marker_opacity=0.85,
            marker_line_width=1.5,
            marker_line_color=line_color,
            hovertemplate="<b>%{text}</b><br>" + cfg["label"] + " : <b>%{z}</b> " + cfg["unit"] + "<extra></extra>"
        ))

        colorbar_bg = "rgba(15, 23, 42, 0.92)" if is_dark else "rgba(255, 255, 255, 0.92)"
        colorbar_border = "#475569" if is_dark else COLORS["border"]
        colorbar_text = "#F3F4F6" if is_dark else COLORS["text_secondary"]

        fig.update_layout(
            map_style=map_style,
            map_zoom=6.0,
            map_center={"lat": 8.65, "lon": 1.05},
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(
                title=dict(text=cfg["unit"], font=dict(size=11, color=colorbar_text)),
                tickfont=dict(size=10, color=colorbar_text),
                thickness=12,
                len=0.72,
                bgcolor=colorbar_bg,
                bordercolor=colorbar_border,
                borderwidth=1
            )
        )
        
        # Panneau de détail latéral
        target_reg = selected_region if selected_region != "ALL" else "MARITIME"
        row_target = df_reg[df_reg["region"] == target_reg].iloc[0]
        
        status_class = "favorable" if row_target["statut"] == "Favorable" else ("intermediaire" if row_target["statut"] == "Intermédiaire" else "deficit")
        
        detail_panel = html.Div(
            className="card-box",
            style={"height": "100%"},
            children=[
                html.Div(className="card-header", children=[
                    html.Div("PROFIL TERRITORIAL", className="card-question"),
                    html.H3(f"Région {row_target['region_label']}", className="card-title"),
                    html.Div(style={"marginTop": "6px"}, children=[
                        html.Span(f"Diagnostic : {row_target['statut']}", className=f"status-pill {status_class}")
                    ])
                ]),
                html.Div(style={"display": "flex", "flexDirection": "column", "gap": "14px"}, children=[
                    html.Div([
                        html.Div("Démographie officielle (2022)", style={"fontSize": "11px", "color": "var(--text-muted)", "fontWeight": "600"}),
                        html.Div(f"{row_target['population']:,.0f} habitants".replace(",", " "), style={"fontSize": "18px", "fontWeight": "700", "color": "var(--text-primary)"})
                    ]),
                    html.Div([
                        html.Div("Points d'agents Mobile Money", style={"fontSize": "11px", "color": "var(--text-muted)", "fontWeight": "600"}),
                        html.Div(f"{row_target['nb_agents']:,.0f} agents actifs".replace(",", " "), style={"fontSize": "16px", "fontWeight": "600", "color": COLORS["violet"] if not is_dark else "#A78BFA"}),
                        html.Div(f"Ratio : {row_target['agents_pour_10000_hab']:.1f} agents / 10k hab (1 agent pour {row_target['habitants_par_agent']:.0f} hab)", style={"fontSize": "12px", "color": "var(--text-secondary)"})
                    ]),
                    html.Div([
                        html.Div("Établissements financiers physiques", style={"fontSize": "11px", "color": "var(--text-muted)", "fontWeight": "600"}),
                        html.Div(f"{row_target['nb_etablissements']} agences (banques / microfinances)", style={"fontSize": "16px", "fontWeight": "600", "color": COLORS["vert"] if not is_dark else "#22C55E"}),
                        html.Div(f"Ratio : {row_target['etab_pour_10000_hab']:.2f} agences / 10k hab (1 agence pour {row_target['habitants_par_etab']:,.0f} hab)".replace(",", " "), style={"fontSize": "12px", "color": "var(--text-secondary)"})
                    ]),
                    html.Div(className="observation-box", style={"marginTop": "8px"}, children=[
                        html.Div("Écart à la moyenne nationale :", style={"fontWeight": "600", "marginBottom": "4px", "color": "var(--text-primary)"}),
                        html.P(f"• Densité Mobile Money : {row_target['ecart_agents_pct']:+.1f}% vs Togo"),
                        html.P(f"• Densité Agences bancaires : {row_target['ecart_etab_pct']:+.1f}% vs Togo")
                    ])
                ])
            ]
        )
        
        # Tableau benchmark
        table_rows = []
        for _, r in df_reg.iterrows():
            st_cls = "favorable" if r["statut"] == "Favorable" else ("intermediaire" if r["statut"] == "Intermédiaire" else "deficit")
            table_rows.append(
                html.Tr([
                    html.Td(html.B(r["region_label"])),
                    html.Td(f"{r['population']:,.0f}".replace(",", " ")),
                    html.Td(f"{r['nb_agents']:,.0f}".replace(",", " ")),
                    html.Td(html.B(f"{r['agents_pour_10000_hab']:.1f}")),
                    html.Td(f"1 pour {r['habitants_par_agent']:.0f}"),
                    html.Td(f"{r['nb_etablissements']:,.0f}"),
                    html.Td(html.B(f"{r['etab_pour_10000_hab']:.2f}")),
                    html.Td(f"1 pour {r['habitants_par_etab']:,.0f}".replace(",", " ")),
                    html.Td(html.Span(r["statut"], className=f"status-pill {st_cls}"))
                ])
            )
            
        table_comp = html.Table(
            className="data-table-simple",
            children=[
                html.Thead(html.Tr([
                    html.Th("Région"),
                    html.Th("Population"),
                    html.Th("Agents MM"),
                    html.Th("Agents / 10k"),
                    html.Th("Habitants / Agent"),
                    html.Th("Agences Finance"),
                    html.Th("Agences / 10k"),
                    html.Th("Habitants / Agence"),
                    html.Th("Diagnostic")
                ])),
                html.Tbody(table_rows)
            ]
        )
        
        return fig, detail_panel, table_comp
