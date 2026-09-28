"""
validate_data.py
================
Analyse exploratoire automatique de chaque dataset brut.

Produit un rapport de diagnostic par dataset :
    - dimensions
    - colonnes et types
    - valeurs nulles
    - doublons
    - modalités catégorielles
    - min/max pour les colonnes numériques
    - années disponibles
    - anomalies détectées automatiquement

Aucune transformation n'est effectuée.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def _null_report(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne un DataFrame avec le nombre et % de nulls par colonne."""
    null_counts = df.isna().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    return pd.DataFrame({"null_count": null_counts, "null_pct": null_pct})


def _detect_anomalies(df: pd.DataFrame, dataset_name: str) -> list[str]:
    """
    Détecte automatiquement des anomalies potentielles dans un DataFrame.
    Retourne une liste de messages d'avertissement.
    Ne modifie pas les données.
    """
    warnings = []

    for col in df.columns:
        # Colonnes supposées numériques
        if pd.api.types.is_numeric_dtype(df[col]):
            # Valeurs négatives impossibles (abonnés, population, etc.)
            neg_mask = df[col] < 0
            if neg_mask.any():
                warnings.append(
                    f"  [WARN] [{col}] : {neg_mask.sum()} valeur(s) negative(s) detectee(s)"
                )

            # Pourcentages > 100 (sauf colonne spécifiquement autorisée)
            if any(kw in col.lower() for kw in ["%", "pct", "pénétration", "part", "taux", "télédensité"]):
                over100 = df[col] > 100
                if over100.any():
                    warnings.append(
                        f"  [WARN] [{col}] : {over100.sum()} valeur(s) > 100 pour un indicateur en % apparent"
                    )

        # Colonnes textuelles : espaces parasites, encodage suspect
        if df[col].dtype == object:
            sample = df[col].dropna().astype(str)
            # Espaces superflus en tête/queue
            stripped_diff = sample[sample != sample.str.strip()]
            if len(stripped_diff) > 0:
                warnings.append(
                    f"  [WARN] [{col}] : {len(stripped_diff)} valeur(s) avec espaces superflus en tete/queue"
                )
            # Caractères de remplacement d'encodage
            bad_enc = sample[sample.str.contains("ï¿½|â€|Ã", na=False, regex=True)]
            if len(bad_enc) > 0:
                warnings.append(
                    f"  [WARN] [{col}] : {len(bad_enc)} valeur(s) avec caracteres suspects (probleme encodage possible)"
                )

    # Vérifications spécifiques pour le dataset télécom (ARPU)
    if dataset_name == "telecom" and "Value" in df.columns and "indicateur" in df.columns:
        arpu_rows = df[df["indicateur"].str.contains("ARPU", na=False, case=False)]
        if not arpu_rows.empty:
            arpu_vals = pd.to_numeric(arpu_rows["Value"], errors="coerce")
            arpu_mean = arpu_vals.mean()
            warnings.append(
                f"  [WARN] [ARPU segment mobile GSM] : valeurs brutes = {arpu_vals.tolist()} "
                f"(unite indiquee: Francs CFA). Valeur moyenne ~ {arpu_mean:,.0f} FCFA. "
                f"Un ARPU mensuel typique est de l'ordre de quelques milliers de FCFA. "
                f"L'ordre de grandeur observe (~10^13) est anormalement eleve. "
                f"ANOMALIE CONSERVEE - verification requise aupres de la source."
            )

    return warnings


def _categorical_modes(df: pd.DataFrame, max_categories: int = 20) -> dict:
    """Retourne les modalités des colonnes catégorielles (si < max_categories valeurs distinctes)."""
    result = {}
    for col in df.select_dtypes(include="object").columns:
        n_unique = df[col].nunique(dropna=True)
        if n_unique <= max_categories:
            result[col] = df[col].value_counts(dropna=False).to_dict()
    return result


def diagnose(df: pd.DataFrame, name: str) -> dict:
    """
    Effectue le diagnostic complet d'un DataFrame.
    Retourne un dictionnaire de résultats.
    """
    report = {}
    report["dataset"] = name
    report["n_rows"] = len(df)
    report["n_cols"] = len(df.columns)
    report["columns"] = list(df.columns)
    report["dtypes"] = {col: str(df[col].dtype) for col in df.columns}
    report["null_report"] = _null_report(df).to_dict()
    report["n_duplicates"] = int(df.duplicated().sum())
    report["n_unique_per_col"] = {col: int(df[col].nunique(dropna=True)) for col in df.columns}

    # Min/max pour colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    report["numeric_stats"] = {}
    for col in numeric_cols:
        report["numeric_stats"][col] = {
            "min": float(df[col].min()) if not df[col].isna().all() else None,
            "max": float(df[col].max()) if not df[col].isna().all() else None,
            "mean": float(df[col].mean()) if not df[col].isna().all() else None,
        }

    # Années disponibles
    date_candidates = [c for c in df.columns if c.lower() in ("date", "year", "annee", "année")]
    report["years_available"] = []
    for dc in date_candidates:
        years = pd.to_numeric(df[dc], errors="coerce").dropna().unique()
        report["years_available"] = sorted([int(y) for y in years])

    # Unités disponibles
    unit_candidates = [c for c in df.columns if c.lower() in ("unit", "unité", "unite")]
    report["units_available"] = []
    for uc in unit_candidates:
        report["units_available"] = df[uc].dropna().unique().tolist()

    # Modalités catégorielles
    report["categorical_modes"] = _categorical_modes(df)

    # Anomalies
    report["anomalies"] = _detect_anomalies(df, name)

    return report


def print_report(report: dict) -> None:
    """Affiche un rapport de diagnostic de façon lisible."""
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  DATASET : {report['dataset'].upper()}")
    print(sep)
    print(f"  Dimensions        : {report['n_rows']} lignes x {report['n_cols']} colonnes")
    print(f"  Doublons exacts   : {report['n_duplicates']}")
    print()
    print("  COLONNES & TYPES :")
    for col in report["columns"]:
        dtype = report["dtypes"][col]
        n_null = report["null_report"]["null_count"].get(col, 0)
        pct_null = report["null_report"]["null_pct"].get(col, 0.0)
        n_uniq = report["n_unique_per_col"].get(col, "?")
        print(f"    {col:<45} {dtype:<12} nulls={n_null} ({pct_null}%)  unique={n_uniq}")

    if report["years_available"]:
        print(f"\n  ANNEES DISPONIBLES : {report['years_available']}")

    if report["units_available"]:
        print(f"  UNITES             : {report['units_available']}")

    if report["categorical_modes"]:
        print("\n  MODALITES CATEGORIELLES (colonnes <= 20 valeurs distinctes) :")
        for col, counts in report["categorical_modes"].items():
            print(f"    {col} :")
            for val, cnt in counts.items():
                print(f"      {str(val):<40} -> {cnt}")

    if report.get("numeric_stats"):
        print("\n  STATISTIQUES NUMERIQUES :")
        for col, stats in report["numeric_stats"].items():
            print(f"    {col:<45} min={stats['min']}  max={stats['max']}  mean={round(stats['mean'],2) if stats['mean'] else None}")

    if report["anomalies"]:
        print("\n  ANOMALIES DETECTEES :")
        for a in report["anomalies"]:
            print(a)
    else:
        print("\n  Aucune anomalie automatique detectee.")


def run_diagnostics(datasets: dict[str, pd.DataFrame]) -> dict[str, dict]:
    """Lance le diagnostic sur tous les datasets et retourne les rapports."""
    reports = {}
    for name, df in datasets.items():
        report = diagnose(df, name)
        print_report(report)
        reports[name] = report
    return reports


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from load_data import load_all
    dfs = load_all()
    run_diagnostics(dfs)
