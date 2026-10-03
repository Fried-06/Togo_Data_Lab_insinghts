"""
app.py
======
TOGO DIGITAL INSIGHT
Observatoire interactif de l'inclusion numerique et financiere au Togo.

Point d'entree principal Dash avec support de 4 themes visuels.
"""

from dash import Dash, html, dcc, Input, Output, State, ctx
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from components.navbar import create_header
from components.footer import create_footer

# Import des 8 pages (ajout de methodology)
from pages import (
    overview,
    internet,
    connectivity,
    territories,
    finance,
    diagnostic,
    recommendations,
    methodology
)

# Initialisation de l'application Dash
app = Dash(
    __name__,
    title="TOGO DIGITAL INSIGHT - Observatoire de l'Inclusion Numerique et Financiere",
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

# Correspondance theme -> classe CSS
THEME_CLASS_MAP = {
    "light":  "theme-light",
    "dark":   "theme-dark",
    "ocean":  "theme-ocean",
    "savane": "theme-savane",
}

# Structure globale de l'application
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


# -----------------------------------------------------------------
# Callback 1 : Mise a jour du theme depuis le selecteur dropdown
# -----------------------------------------------------------------
@app.callback(
    Output("theme-store", "data"),
    [Input("theme-selector-dropdown", "value"),
     Input("theme-toggle-btn", "n_clicks")],
    State("theme-store", "data"),
    prevent_initial_call=True
)
def update_theme(dropdown_value, toggle_clicks, current_theme):
    """
    Deux declencheurs :
    - theme-selector-dropdown : selecteur explicite parmi 4 themes
    - theme-toggle-btn        : bascule rapide clair <-> sombre
    """
    triggered = ctx.triggered_id
    if triggered == "theme-selector-dropdown" and dropdown_value:
        return dropdown_value
    if triggered == "theme-toggle-btn":
        # Bascule: si actif = light/ocean/savane -> dark, si dark -> light
        return "dark" if current_theme != "dark" else "light"
    return current_theme or "light"


# -----------------------------------------------------------------
# Callback 2 : Classe CSS globale selon le theme
# -----------------------------------------------------------------
@app.callback(
    Output("app-root", "className"),
    Input("theme-store", "data")
)
def update_root_theme_class(theme_data):
    return THEME_CLASS_MAP.get(theme_data, "theme-light")


# -----------------------------------------------------------------
# Callback 3 : Routage et affichage de la page + header
# -----------------------------------------------------------------
@app.callback(
    [Output("page-content", "children"),
     Output("header-container", "children")],
    [Input("url", "pathname"),
     Input("theme-store", "data")]
)
def display_page(pathname, theme_data):
    is_dark = (theme_data == "dark")
    theme = theme_data or "light"
    active_path = pathname if pathname else "/"

    route_map = {
        "/":               overview.layout,
        "/internet":       internet.layout,
        "/connectivity":   connectivity.layout,
        "/territories":    territories.layout,
        "/finance":        finance.layout,
        "/diagnostic":     diagnostic.layout,
        "/recommendations": recommendations.layout,
        "/methodology":    methodology.layout,
    }

    layout_fn = route_map.get(active_path)
    if layout_fn:
        content = layout_fn()
    else:
        content = html.Div(
            className="main-container",
            style={"textAlign": "center", "padding": "80px 20px"},
            children=[
                html.H2(
                    "Page non trouvee (404)",
                    style={"fontSize": "28px", "fontWeight": "700",
                           "color": "var(--text-primary)", "marginBottom": "12px"}
                ),
                html.P(
                    "La section demandee n'existe pas dans l'observatoire.",
                    style={"color": "var(--text-muted)", "marginBottom": "24px"}
                ),
                dcc.Link("Retourner a la Vue d'ensemble", href="/", className="nav-tab-item active")
            ]
        )

    header = create_header(active_path=active_path, is_dark=is_dark, theme=theme)
    return content, header


if __name__ == "__main__":
    print("=" * 80)
    print("  TOGO DIGITAL INSIGHT - Demarrage du serveur Dash...")
    print("  Acces local : http://127.0.0.1:8050/")
    print("=" * 80)
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False)
