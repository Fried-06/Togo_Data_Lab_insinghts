"""
utils/data_loader.py
===================
Gestionnaire de chargement et de mise en cache mémoire des datasets préparés.
Évite la relecture disque répétée à chaque callback Dash.
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

# Répertoire racine du projet
ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUT_DIR = ROOT_DIR / "data" / "output"
ASSETS_DIR = ROOT_DIR / "assets"

# Dictionnaire de cache en mémoire
_CACHE = {}

def get_geojson_regions():
    """Charge le fichier GeoJSON des 5 régions administratives du Togo."""
    if "togo_regions_geojson" not in _CACHE:
        geojson_path = ASSETS_DIR / "togo_regions.geojson"
        if not geojson_path.exists():
            geojson_path = ROOT_DIR / "data" / "togo_regions.geojson"
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _CACHE["togo_regions_geojson"] = data
    return _CACHE["togo_regions_geojson"]

def get_territorial_access():
    """Charge la table d'accès territorial (data/output/territorial_access.csv)."""
    if "territorial_access" not in _CACHE:
        path = OUTPUT_DIR / "territorial_access.csv"
        df = pd.read_csv(path)
        # Harmonisation avec les 5 régions GeoJSON
        _CACHE["territorial_access"] = df
    return _CACHE["territorial_access"].copy()

def get_internet_tech():
    """Charge le dataset des technologies Internet (data/processed/internet_tech_clean.csv)."""
    if "internet_tech" not in _CACHE:
        path = PROCESSED_DIR / "internet_tech_clean.csv"
        df = pd.read_csv(path)
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
        _CACHE["internet_tech"] = df
    return _CACHE["internet_tech"].copy()

def get_internet_users():
    """Charge l'indicateur d'utilisation d'Internet Banque Mondiale/ITU."""
    if "internet_users" not in _CACHE:
        path = PROCESSED_DIR / "internet_users_clean.csv"
        df = pd.read_csv(path)
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
        _CACHE["internet_users"] = df
    return _CACHE["internet_users"].copy()

def get_telecom():
    """Charge le dataset télécommunications ARCEP (data/processed/telecom_clean.csv)."""
    if "telecom" not in _CACHE:
        path = PROCESSED_DIR / "telecom_clean.csv"
        df = pd.read_csv(path)
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
        _CACHE["telecom"] = df
    return _CACHE["telecom"].copy()

def get_mobile_money_clean():
    """Charge le dataset brut des points d'agents Mobile Money."""
    if "mobile_money_clean" not in _CACHE:
        path = PROCESSED_DIR / "mobile_money_clean.csv"
        # Chargement des colonnes nécessaires pour économiser la mémoire
        cols = ["FID", "region_normalisee", "prefecture_normalisee", "commune_normalisee", "operateur", "longitude", "latitude"]
        df = pd.read_csv(path, usecols=cols)
        _CACHE["mobile_money_clean"] = df
    return _CACHE["mobile_money_clean"].copy()

def get_finance_clean():
    """Charge le dataset des établissements financiers."""
    if "finance_clean" not in _CACHE:
        path = PROCESSED_DIR / "finance_clean.csv"
        df = pd.read_csv(path)
        _CACHE["finance_clean"] = df
    return _CACHE["finance_clean"].copy()

def get_finance_territories():
    """Charge les agrégats de la finance par région et catégorie."""
    if "finance_territories" not in _CACHE:
        p_reg = PROCESSED_DIR / "finance_territories_region.csv"
        p_cat = PROCESSED_DIR / "finance_territories_cat_region.csv"
        p_pref = PROCESSED_DIR / "finance_territories_prefecture.csv"
        _CACHE["finance_territories"] = {
            "region": pd.read_csv(p_reg),
            "cat_region": pd.read_csv(p_cat),
            "prefecture": pd.read_csv(p_pref)
        }
    return _CACHE["finance_territories"]

def get_mm_territories():
    """Charge les agrégats Mobile Money par région, préfecture, commune."""
    if "mm_territories" not in _CACHE:
        p_reg = PROCESSED_DIR / "mobile_money_territories_region.csv"
        p_pref = PROCESSED_DIR / "mobile_money_territories_prefecture.csv"
        p_com = PROCESSED_DIR / "mobile_money_territories_commune.csv"
        _CACHE["mm_territories"] = {
            "region": pd.read_csv(p_reg),
            "prefecture": pd.read_csv(p_pref),
            "commune": pd.read_csv(p_com)
        }
    return _CACHE["mm_territories"]

def get_population_territories():
    """Charge le découpage démographique officiel 2022."""
    if "population_territories" not in _CACHE:
        path = PROCESSED_DIR / "population_territories.csv"
        _CACHE["population_territories"] = pd.read_csv(path)
    return _CACHE["population_territories"].copy()
