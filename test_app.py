"""
test_app.py
===========
Validation et tests d'intégrité de l'application Togo Digital Insight :
- Chargement des données
- Rendu des 7 pages
- Exécution des callbacks
- Vérification du GeoJSON
- Bascule Mode Clair / Mode Sombre
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.data_loader import (
    get_territorial_access,
    get_internet_users,
    get_internet_tech,
    get_telecom,
    get_finance_clean,
    get_mobile_money_clean,
    get_geojson_regions
)
from utils.calculations import get_overview_kpis, get_consolidated_regions_data, get_prefectures_summary
from pages import overview, internet, connectivity, territories, finance, diagnostic, recommendations
from app import app, display_page, toggle_theme, update_root_theme_class

def run_tests():
    print("=" * 70)
    print("  TESTS D'INTÉGRITÉ — TOGO DIGITAL INSIGHT")
    print("=" * 70)
    
    # 1. Données
    print("\n[1/5] Vérification du chargement des datasets...")
    assert len(get_territorial_access()) > 0, "territorial_access vide"
    assert len(get_internet_users()) > 0, "internet_users vide"
    assert len(get_internet_tech()) > 0, "internet_tech vide"
    assert len(get_telecom()) > 0, "telecom vide"
    assert len(get_finance_clean()) > 0, "finance_clean vide"
    assert len(get_mobile_money_clean()) > 0, "mobile_money_clean vide"
    gj = get_geojson_regions()
    assert len(gj["features"]) == 5, f"GeoJSON attend 5 régions, trouvé {len(gj['features'])}"
    print("  -> Datasets et GeoJSON chargés avec succès (5 régions validées).")
    
    # 2. Calculs
    print("\n[2/5] Vérification des modules de calculs...")
    kpis = get_overview_kpis()
    assert "internet_penetration" in kpis
    assert "mm_agents" in kpis
    reg_df = get_consolidated_regions_data()
    assert len(reg_df) == 5, f"Attend 5 régions consolidées, trouvé {len(reg_df)}"
    pref_df = get_prefectures_summary()
    assert len(pref_df) >= 35, f"Attend >= 35 préfectures, trouvé {len(pref_df)}"
    print(f"  -> KPI, 5 régions et {len(pref_df)} préfectures consolidées avec succès.")
    
    # 3. Rendu des layouts
    print("\n[3/5] Vérification du rendu HTML/Dash des 7 pages...")
    for p_name, mod in [
        ("Vue d'ensemble", overview),
        ("Internet", internet),
        ("Connectivité", connectivity),
        ("Territoires", territories),
        ("Finance", finance),
        ("Diagnostic", diagnostic),
        ("Recommandations", recommendations)
    ]:
        layout = mod.layout()
        assert layout is not None
        print(f"  -> Page {p_name} : OK")
    
    # 4. Mode Clair / Mode Sombre
    print("\n[4/5] Vérification de la bascule Mode Clair / Mode Sombre...")
    t1 = toggle_theme(1, "light")
    assert t1 == "dark", f"Attend 'dark', obtenu {t1}"
    t2 = toggle_theme(2, "dark")
    assert t2 == "light", f"Attend 'light', obtenu {t2}"
    cls_dark = update_root_theme_class("dark")
    assert cls_dark == "theme-dark"
    cls_light = update_root_theme_class("light")
    assert cls_light == "theme-light"
    print("  -> Toggle theme et classes CSS : OK")
    
    # 5. Routeur & Pages
    print("\n[5/5] Vérification du serveur Dash principal et du routeur...")
    out_page, out_header = display_page("/", "light")
    assert out_page is not None
    assert out_header is not None
    out_page_dark, out_header_dark = display_page("/connectivity", "dark")
    assert out_page_dark is not None
    assert out_header_dark is not None
    print("  -> Routeur en modes Clair et Sombre : OK")
    
    print("\n" + "=" * 70)
    print("  TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS (100% FONCTIONNEL)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
