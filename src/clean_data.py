"""
clean_data.py
=============
Nettoyage et normalisation de chaque dataset.

Principes :
    - Les fichiers sources ne sont JAMAIS modifiés.
    - Chaque correction est documentée en commentaire et dans QUALITY_LOG.
    - NaN != 0 : aucune valeur manquante n'est remplacée par 0 sans justification explicite.
    - Les colonnes originales sont conservées ; les colonnes normalisées sont ajoutées avec suffixe.
    - Les anomalies non corrigibles sont signalées dans QUALITY_LOG.

QUALITY_LOG : liste de dicts { dataset, colonne, probleme, decision, justification }
"""

from pathlib import Path
import pandas as pd
import numpy as np
import re

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Journal qualité global
QUALITY_LOG: list[dict] = []


def _log(dataset: str, colonne: str, probleme: str, decision: str, justification: str):
    entry = {
        "dataset": dataset,
        "colonne": colonne,
        "probleme": probleme,
        "decision": decision,
        "justification": justification,
    }
    QUALITY_LOG.append(entry)
    print(f"  [LOG] {dataset} | {colonne} | {probleme[:60]}")


# ---------------------------------------------------------------------------
# Utilitaires géographiques
# ---------------------------------------------------------------------------

def normalize_geo_name(s: str) -> str:
    """
    Normalisation minimale d'un nom géographique :
        - strip des espaces
        - conversion en majuscules
        - suppression des tirets doublés, espaces multiples
    Conserve les accents car la base a des noms cohérents.
    Ne modifie pas la colonne originale.
    """
    if not isinstance(s, str):
        return s
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.upper()
    return s


# ---------------------------------------------------------------------------
# Nettoyage Population
# ---------------------------------------------------------------------------

def clean_population(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    # 1. Renommage colonnes
    clean.columns = [
        "indicateur", "decoupage_administratif", "sexe", "unit", "annee", "valeur"
    ]
    _log("population", "toutes", "Colonnes avec accents/tirets", "Renommage sans accent/tiret",
         "Facilite l'usage Python sans modifier les donnees")

    # 2. annee -> int
    clean["annee"] = pd.to_numeric(clean["annee"], errors="coerce").astype("Int64")
    _log("population", "annee", "Type objet/string", "Conversion en Int64",
         "La Date represente une annee entiere")

    # 3. valeur -> int
    clean["valeur"] = pd.to_numeric(clean["valeur"], errors="coerce").astype("Int64")
    _log("population", "valeur", "Type objet/string", "Conversion en Int64",
         "Population = nombre entier")

    # 4. Trim espaces dans colonnes textuelles
    for col in ["indicateur", "decoupage_administratif", "sexe", "unit"]:
        original_with_spaces = clean[col].dropna().astype(str).str.strip() != clean[col].dropna().astype(str)
        n_stripped = original_with_spaces.sum()
        clean[col] = clean[col].astype(str).str.strip()
        if n_stripped > 0:
            _log("population", col, f"{n_stripped} valeurs avec espaces superflus",
                 "str.strip() applique", "Normalisation basique")

    # 5. Colonne géographique normalisée (majuscules, trim)
    clean["geo_normalisee"] = clean["decoupage_administratif"].apply(normalize_geo_name)
    _log("population", "decoupage_administratif", "Casse/espaces heterogenes",
         "Ajout colonne geo_normalisee (MAJ, strip) - originale meinteneue",
         "Permet les jointures sans detruire la source")

    # 6. Doublons géographiques
    dup_geo = clean[clean.duplicated(subset=["decoupage_administratif", "sexe", "annee"], keep=False)]
    if len(dup_geo) > 0:
        _log("population", "decoupage_administratif",
             f"{len(dup_geo)} lignes partagent le meme nom geographique + sexe + annee",
             "Conservees - niveaux administratifs differents (ex: CINKASSE prefecture vs commune)",
             "Une suppression aveugle ferait perdre un niveau administratif reel")

    # 7. Doublons exacts
    n_dup_exact = clean.duplicated().sum()
    if n_dup_exact > 0:
        clean = clean.drop_duplicates()
        _log("population", "toutes", f"{n_dup_exact} doublons exacts",
             f"Suppression de {n_dup_exact} doublons exacts",
             "Lignes identiques sur toutes les colonnes")

    print(f"  population : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Nettoyage Télécom
# ---------------------------------------------------------------------------

def clean_telecom(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    # 1. Renommage
    clean.columns = ["indicateur", "unit", "annee", "valeur"]

    # 2. Trim noms d'indicateurs
    clean["indicateur"] = clean["indicateur"].astype(str).str.strip()

    # 3. annee -> int
    clean["annee"] = pd.to_numeric(clean["annee"], errors="coerce").astype("Int64")
    _log("telecom", "annee", "Type string", "Conversion Int64", "Annee entiere")

    # 4. valeur -> float
    clean["valeur"] = pd.to_numeric(clean["valeur"], errors="coerce")
    _log("telecom", "valeur", "Type string mixte", "Conversion float",
         "Indicateurs numeriques (abonnes, %, FCFA)")

    # 5. Documentation anomalie ARPU
    arpu_mask = clean["indicateur"].str.contains("ARPU", case=False, na=False)
    arpu_data = clean[arpu_mask]
    if not arpu_data.empty:
        arpu_min = arpu_data["valeur"].min()
        arpu_max = arpu_data["valeur"].max()
        _log(
            "telecom",
            "ARPU segment mobile GSM",
            f"Valeurs brutes entre {arpu_min:.2e} et {arpu_max:.2e} FCFA. "
            f"L'ordre de grandeur observe (~10^13) est ANORMALEMENT eleve. ",
            "ANOMALIE CONSERVEE - valeur brute inchangee",
            "Aucune source fiable ne permet de corriger."
        )
        clean["arpu_anomalie_flag"] = False
        clean.loc[arpu_mask, "arpu_anomalie_flag"] = True

    # 6. Parts de marché
    pm_mask = clean["indicateur"].str.contains("Part de marché", case=False, na=False)
    pm_data = clean[pm_mask].copy()
    if not pm_data.empty:
        pm_sum = pm_data.groupby("annee")["valeur"].sum()
        for annee, total in pm_sum.items():
            if abs(total - 100) > 1.0:
                _log("telecom", "Part de marche",
                     f"Annee {annee} : somme des parts de marche = {total:.2f}% != 100%",
                     "Signalement uniquement - donnees meinteneues",
                     "Arrondis ou transition")

    # 7. Doublons exacts
    n_dup = clean.duplicated().sum()
    if n_dup > 0:
        clean = clean.drop_duplicates()
        _log("telecom", "toutes", f"{n_dup} doublons exacts", "Suppression", "Redondance certaine")

    print(f"  telecom : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Nettoyage Internet Technologies
# ---------------------------------------------------------------------------

def clean_internet_tech(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    clean.columns = ["indicateur", "unit", "annee", "valeur"]
    clean["indicateur"] = clean["indicateur"].astype(str).str.strip()
    clean["annee"] = pd.to_numeric(clean["annee"], errors="coerce").astype("Int64")
    clean["valeur"] = pd.to_numeric(clean["valeur"], errors="coerce")

    # Incohérence unité pour taux de pénétration
    pen_mask = clean["indicateur"].str.contains("Taux de pénétration", case=False, na=False)
    if pen_mask.any():
        _log(
            "internet_tech",
            "Taux de penetration Internet",
            "Unit='Nombre' mais valeurs en %",
            "Ajout colonne 'unit_corrigee'='Pourcentage' - valeur brute meinteneue",
            "Indicateurs en pourcentage"
        )
        clean["unit_corrigee"] = clean["unit"]
        clean.loc[pen_mask, "unit_corrigee"] = "Pourcentage"

    def _clean_label(label: str) -> str:
        label = re.sub(r"^T\s+([A-Z])", r"Total \1", label)
        label = re.sub(r"^T\s+([a-z])", r"Total \1", label)
        return label.strip()

    clean["indicateur_propre"] = clean["indicateur"].apply(_clean_label)

    zero_count = (clean["valeur"] == 0).sum()
    _log("internet_tech", "valeur",
         f"{zero_count} valeurs a 0 dans la source",
         "Valeurs 0 meinteneues telles quelles",
         "0 abonnee reel")

    n_dup = clean.duplicated().sum()
    if n_dup > 0:
        clean = clean.drop_duplicates()

    print(f"  internet_tech : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Nettoyage Internet Users
# ---------------------------------------------------------------------------

def clean_internet_users(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    clean = clean.rename(columns={
        "indicator": "indicateur",
        "country": "pays",
        "countryiso3code": "iso3",
        "date": "annee",
        "value": "valeur",
        "unit": "unit",
        "obs_status": "statut_obs",
        "decimal": "decimal"
    })

    clean["annee"] = pd.to_numeric(clean["annee"], errors="coerce").astype("Int64")
    clean["valeur"] = pd.to_numeric(clean["valeur"], errors="coerce")

    n_missing = clean["valeur"].isna().sum()
    _log("internet_users", "valeur",
         f"{n_missing} valeurs manquantes",
         "NaN meinteneus", "Absence de mesure")

    n_dup = clean.duplicated().sum()
    if n_dup > 0:
        clean = clean.drop_duplicates()

    print(f"  internet_users : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Nettoyage Mobile Money
# ---------------------------------------------------------------------------

def clean_mobile_money(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    geo_cols = ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd"]
    for col in geo_cols:
        if col in clean.columns:
            clean[col] = clean[col].astype(str).str.strip().replace("nan", pd.NA)

    for col in geo_cols:
        norm_col = col.replace("_nom_bdd", "_normalisee")
        clean[norm_col] = clean[col].apply(lambda x: normalize_geo_name(str(x)) if pd.notna(x) else pd.NA)

    def _extract_coords(geom_str):
        if not isinstance(geom_str, str):
            return pd.NA, pd.NA
        m = re.match(r"POINT\s*\(([0-9.\-]+)\s+([0-9.\-]+)\)", geom_str.strip())
        if m:
            return float(m.group(1)), float(m.group(2))
        return pd.NA, pd.NA

    coords = clean["geometry"].apply(_extract_coords)
    clean["longitude"] = [c[0] for c in coords]
    clean["latitude"] = [c[1] for c in coords]

    if "operateur" in clean.columns:
        clean["operateur"] = clean["operateur"].astype(str).str.strip()

    clean["date_collecte"] = "2024-12-19"

    n_dup = clean.duplicated().sum()
    if n_dup > 0:
        clean = clean.drop_duplicates()

    print(f"  mobile_money : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Nettoyage Établissements Financiers
# ---------------------------------------------------------------------------

def clean_finance(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    n_before = len(clean)

    text_cols = ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd",
                 "canton_nom_bdd", "nom_localite", "etab_nom", "activite_categorie"]
    for col in text_cols:
        if col in clean.columns:
            clean[col] = clean[col].astype(str).str.strip().replace("nan", pd.NA)

    if "activite_categorie" in clean.columns:
        n_typo = (clean["activite_categorie"] == "Micro-Finace").sum()
        n_correct = (clean["activite_categorie"] == "Micro-Finance").sum()
        if n_typo > 0:
            clean["activite_categorie_orig"] = clean["activite_categorie"].copy()
            clean["activite_categorie"] = clean["activite_categorie"].replace("Micro-Finace", "Micro-Finance")
            _log(
                "finance",
                "activite_categorie",
                f"'Micro-Finace' : {n_typo} occurrence(s) -> harmonisation Micro-Finance",
                "Correction 'Micro-Finace' -> 'Micro-Finance' avec colonne originale conservee",
                "Faute de frappe manifeste"
            )

    geo_cols = ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd"]
    for col in geo_cols:
        if col in clean.columns:
            norm_col = col.replace("_nom_bdd", "_normalisee")
            clean[norm_col] = clean[col].apply(
                lambda x: normalize_geo_name(str(x)) if (pd.notna(x) and str(x) != "nan") else pd.NA
            )

    def _extract_coords(geom_str):
        if not isinstance(geom_str, str):
            return pd.NA, pd.NA
        m = re.match(r"POINT\s*\(([0-9.\-]+)\s+([0-9.\-]+)\)", geom_str.strip())
        if m:
            return float(m.group(1)), float(m.group(2))
        return pd.NA, pd.NA

    coords = clean["geometry"].apply(_extract_coords)
    clean["longitude"] = [c[0] for c in coords]
    clean["latitude"] = [c[1] for c in coords]

    clean["date_collecte"] = "2025-01-08"

    n_dup = clean.duplicated().sum()
    if n_dup > 0:
        clean = clean.drop_duplicates()

    print(f"  finance : {n_before} -> {len(clean)} lignes")
    return clean


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def clean_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {}

    print("\n--- Nettoyage population ---")
    cleaned["population"] = clean_population(datasets["population"])

    print("\n--- Nettoyage telecom ---")
    cleaned["telecom"] = clean_telecom(datasets["telecom"])

    print("\n--- Nettoyage internet_tech ---")
    cleaned["internet_tech"] = clean_internet_tech(datasets["internet_tech"])

    print("\n--- Nettoyage internet_users ---")
    cleaned["internet_users"] = clean_internet_users(datasets["internet_users"])

    print("\n--- Nettoyage mobile_money ---")
    cleaned["mobile_money"] = clean_mobile_money(datasets["mobile_money"])

    print("\n--- Nettoyage finance ---")
    cleaned["finance"] = clean_finance(datasets["finance"])

    return cleaned


def get_quality_log() -> list[dict]:
    return QUALITY_LOG


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from load_data import load_all
    dfs = load_all()
    cleaned = clean_all(dfs)
