"""
components/footer.py
====================
Pied de page institutionnel de l'observatoire avec sources et section méthodologie.
"""

from dash import html

def create_footer():
    """Crée le pied de page institutionnel et les informations de traçabilité."""
    return html.Footer(
        style={
            "backgroundColor": "var(--surface)",
            "borderTop": "1px solid var(--border)",
            "padding": "32px 24px",
            "marginTop": "40px",
            "fontSize": "13px",
            "color": "var(--text-muted)",
            "transition": "background-color 0.2s ease, border-color 0.2s ease"
        },
        children=[
            html.Div(
                style={"maxWidth": "1400px", "margin": "0 auto", "display": "grid", "gridTemplateColumns": "2fr 1fr 1fr", "gap": "32px"},
                children=[
                    html.Div([
                        html.H4("TOGO DIGITAL INSIGHT — OBSERVATOIRE DE DONNÉES", style={"fontSize": "14px", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "8px"}),
                        html.P(
                            "Outil d'intelligence territoriale et d'aide à la décision publique pour le suivi "
                            "de la connectivité Internet, du déploiement des infrastructures télécoms et de "
                            "la bancarisation numérique au Togo.",
                            style={"lineHeight": "1.5", "marginBottom": "12px", "color": "var(--text-secondary)"}
                        ),
                        html.P("© 2026 TogoAI Labs — Développé selon les principes de transparence et de rigueur statistique.", style={"fontSize": "12px", "color": "var(--text-muted)"})
                    ]),
                    html.Div([
                        html.H4("SOURCES PRIMAIRES", style={"fontSize": "12px", "fontWeight": "700", "color": "var(--text-primary)", "textTransform": "uppercase", "letterSpacing": "0.04em", "marginBottom": "8px"}),
                        html.Ul(
                            style={"listStyle": "none", "padding": 0, "lineHeight": "1.8", "color": "var(--text-secondary)"},
                            children=[
                                html.Li("• INSEED Togo — RGPH-5 (2022)"),
                                html.Li("• ARCEP Togo — Rapports annuels (2013-2019)"),
                                html.Li("• Banque Mondiale / ITU — WDI (1960-2023)"),
                                html.Li("• Données terrain Mobile Money (Déc. 2024)"),
                                html.Li("• Répertoire Établissements Financiers (Jan. 2025)")
                            ]
                        )
                    ]),
                    html.Div([
                        html.H4("CONVENTIONS MÉTHODOLOGIQUES", style={"fontSize": "12px", "fontWeight": "700", "color": "var(--text-primary)", "textTransform": "uppercase", "letterSpacing": "0.04em", "marginBottom": "8px"}),
                        html.Ul(
                            style={"listStyle": "none", "padding": 0, "lineHeight": "1.8", "color": "var(--text-secondary)"},
                            children=[
                                html.Li("• Décalage temporel : millésimes documentés"),
                                html.Li("• ARPU GSM : anomalie brute conservée"),
                                html.Li("• Ratios : calculés uniquement si données > 0"),
                                html.Li("• Normalisation territoriale : 5 régions + 39 préfectures")
                            ]
                        )
                    ])
                ]
            )
        ]
    )
