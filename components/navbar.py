"""
components/navbar.py
====================
Barre de navigation institutionnelle.
Support de 4 themes : Institutionnel (clair), Sombre, Ocean, Savane.
"""

from dash import html, dcc

NAV_ITEMS = [
    {"label": "Vue d'ensemble",    "path": "/"},
    {"label": "Internet",          "path": "/internet"},
    {"label": "Connectivite",      "path": "/connectivity"},
    {"label": "Territoires",       "path": "/territories"},
    {"label": "Finance",           "path": "/finance"},
    {"label": "Diagnostic",        "path": "/diagnostic"},
    {"label": "Recommandations",   "path": "/recommendations"},
    {"label": "Methodologie",      "path": "/methodology"},
]

THEME_OPTIONS = [
    {"label": "Institutionnel", "value": "light"},
    {"label": "Sombre",         "value": "dark"},
    {"label": "Ocean",          "value": "ocean"},
    {"label": "Savane",         "value": "savane"},
]

def create_header(active_path="/", is_dark=False, theme="light"):
    """
    Cree le header complet avec bandeau institutionnel,
    selecteur de theme (4 options) et barre d'onglets.
    """
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

    # Icone visuelle pour le bouton de bascule (CSS pure, pas de SVG)
    toggle_label = "Sombre" if not is_dark else "Clair"
    toggle_icon_class = "toggle-icon mode-clair" if not is_dark else "toggle-icon mode-sombre"

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
                                html.P(
                                    "Observatoire de l'inclusion numerique et financiere au Togo",
                                    className="brand-subtitle"
                                )
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
                                    html.Span("Donnees certifiees - RGPH-5, ARCEP, ITU")
                                ]
                            ),
                            # Selecteur de theme (4 options)
                            html.Div(
                                className="theme-selector-wrapper",
                                children=[
                                    dcc.Dropdown(
                                        id="theme-selector-dropdown",
                                        options=THEME_OPTIONS,
                                        value=theme,
                                        clearable=False,
                                        searchable=False,
                                        style={"width": "148px", "fontSize": "12px"},
                                        className="theme-dropdown"
                                    )
                                ]
                            ),
                            html.Button(
                                id="theme-toggle-btn",
                                className="theme-toggle-btn",
                                title="Basculer mode clair / mode sombre",
                                children=[
                                    html.Span(className=toggle_icon_class),
                                    html.Span(
                                        toggle_label,
                                        id="theme-toggle-label"
                                    )
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
