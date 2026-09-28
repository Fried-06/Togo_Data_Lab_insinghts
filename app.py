"""
app.py
======
TOGO DIGITAL INSIGHT
Observatoire interactif de l'inclusion numérique et financière au Togo.

Point d'entrée principal Dash avec support Mode Clair / Mode Sombre.
"""

from dash import Dash, html, dcc, Input, Output, State
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from components.navbar import create_header
from components.footer import create_footer

# Import des 7 pages
from pages import (
    overview,
    internet,
    connectivity,
    territories,
    finance,
    diagnostic,
    recommendations
)

# Initialisation de l'application Dash
app = Dash(
    __name__,
    title="TOGO DIGITAL INSIGHT — Observatoire de l'Inclusion Numérique & Financière",
    suppress_callback_exceptions=True,
    update_title="Chargement...",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

server = app.server

# Enregistrement des callbacks de chaque page
overview.register_callbacks(app)
internet.register_callbacks(app)
connectivity.register_callbacks(app)
territories.register_callbacks(app)
finance.register_callbacks(app)
diagnostic.register_callbacks(app)

# Structure globale de l'application avec dcc.Store pour le thème
app.layout = html.Div(
    id="app-root",
    className="theme-light",
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        html.Div(id="header-container"),
        html.Main(id="page-content"),
        create_footer()
    ]
)

# Callback pour basculer entre Mode Clair et Mode Sombre
@app.callback(
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    if not n_clicks:
        return current_theme or "light"
    return "dark" if current_theme == "light" else "light"

# Callback pour adapter la classe CSS globale du conteneur #app-root
@app.callback(
    Output("app-root", "className"),
    Input("theme-store", "data")
)
def update_root_theme_class(theme_data):
    return "theme-dark" if theme_data == "dark" else "theme-light"

# Callback de routage et affichage de la page et du header
@app.callback(
    [Output("page-content", "children"),
     Output("header-container", "children")],
    [Input("url", "pathname"),
     Input("theme-store", "data")]
)
def display_page(pathname, theme_data):
    is_dark = (theme_data == "dark")
    active_path = pathname if pathname else "/"

    if not pathname or pathname == "/":
        content = overview.layout()
    elif pathname == "/internet":
        content = internet.layout()
    elif pathname == "/connectivity":
        content = connectivity.layout()
    elif pathname == "/territories":
        content = territories.layout()
    elif pathname == "/finance":
        content = finance.layout()
    elif pathname == "/diagnostic":
        content = diagnostic.layout()
    elif pathname == "/recommendations":
        content = recommendations.layout()
    else:
        content = html.Div(
            className="main-container",
            style={"textAlign": "center", "padding": "80px 20px"},
            children=[
                html.H2("Page non trouvée (404)", style={"fontSize": "28px", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "12px"}),
                html.P("La section demandée n'existe pas dans l'observatoire.", style={"color": "var(--text-muted)", "marginBottom": "24px"}),
                dcc.Link("Retourner à la Vue d'ensemble", href="/", className="nav-tab-item active")
            ]
        )

    return content, create_header(active_path=active_path, is_dark=is_dark)

if __name__ == "__main__":
    print("=" * 80)
    print("  TOGO DIGITAL INSIGHT — Démarrage du serveur Dash...")
    print("  Accès local : http://127.0.0.1:8050/")
    print("=" * 80)
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)
