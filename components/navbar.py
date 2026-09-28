"""
components/navbar.py
====================
Barre de navigation institutionnelle supérieure avec sélection d'onglets et bascule Mode Sombre.
"""

from dash import html, dcc

NAV_ITEMS = [
    {"label": "Vue d'ensemble", "path": "/"},
    {"label": "Internet", "path": "/internet"},
    {"label": "Connectivité", "path": "/connectivity"},
    {"label": "Territoires", "path": "/territories"},
    {"label": "Finance", "path": "/finance"},
    {"label": "Diagnostic", "path": "/diagnostic"},
    {"label": "Recommandations", "path": "/recommendations"},
]

def create_header(active_path="/", is_dark=False):
    """Crée le header complet avec bandeau institutionnel, sélecteur de thème et barre d'onglets."""
    tabs = []
    for item in NAV_ITEMS:
        is_active = (item["path"] == active_path)
        class_name = "nav-tab-item active" if is_active else "nav-tab-item"
        tabs.append(
            dcc.Link(
                item["label"],
                href=item["path"],
                className=class_name
            )
        )

    # Icône et libellé selon mode
    if is_dark:
        theme_icon = "☀️"
        theme_label = "Mode clair"
    else:
        theme_icon = "🌙"
        theme_label = "Mode sombre"

    return html.Header(
        className="header-wrapper",
        children=[
            html.Div(
                className="header-top",
                children=[
                    html.Div(
                        className="brand-section",
                        children=[
                            html.Div(className="brand-flag-badge"),
                            html.Div([
                                html.H1("TOGO DIGITAL INSIGHT", className="brand-title"),
                                html.P("Observatoire interactif de l'inclusion numérique et financière au Togo", className="brand-subtitle")
                            ])
                        ]
                    ),
                    html.Div(
                        className="header-right-actions",
                        children=[
                            html.Div(
                                className="header-status-badge",
                                children=[
                                    html.Span(className="header-status-dot"),
                                    html.Span("Données certifiées • RGPH-5, ARCEP, ITU")
                                ]
                            ),
                            html.Button(
                                id="theme-toggle-btn",
                                className="theme-toggle-btn",
                                title="Basculer entre mode clair et mode sombre",
                                children=[
                                    html.Span(theme_icon, style={"fontSize": "13px"}),
                                    html.Span(theme_label, id="theme-toggle-label")
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Nav(
                className="nav-tabs-wrapper",
                children=tabs
            )
        ]
    )
