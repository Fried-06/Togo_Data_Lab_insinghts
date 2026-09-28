"""
transform_data.py
=================
Construction des datasets analytiques finaux.

Ce module effectue :
    1. Sauvegarde des datasets nettoyés individuels (processed/)
    2. Agrégations géographiques (population, mobile_money, finance)
    3. Construction de la table territorial_access avec indicateurs calculés
    4. Contrôles de cohérence avant/après
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "data" / "output"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Journal des jointures
JOIN_LOG: list[dict] = []


def _log_join(description: str, n_left: int, n_right: int, n_result: int,
              match_rate: float, issues: str = ""):
    entry = {
        "description": description,
        "n_left": n_left,
        "n_right": n_right,
        "n_result": n_result,
        "match_rate_pct": round(match_rate, 2),
        "issues": issues,
    }
    JOIN_LOG.append(entry)
    print(f"  [JOIN] {description}")
    print(f"         left={n_left} | right={n_right} | result={n_result} | match={match_rate:.1f}%")
    if issues:
        print(f"         [WARN] {issues}")


# ---------------------------------------------------------------------------
# 1. Sauvegarde des datasets nettoyés individuels
# ---------------------------------------------------------------------------

def save_cleaned(cleaned: dict[str, pd.DataFrame]) -> None:
    name_map = {
        "population":     "population_clean.csv",
        "telecom":        "telecom_clean.csv",
        "internet_tech":  "internet_tech_clean.csv",
        "internet_users": "internet_users_clean.csv",
        "mobile_money":   "mobile_money_clean.csv",
        "finance":        "finance_clean.csv",
    }
    for key, filename in name_map.items():
        if key in cleaned:
            out_path = PROCESSED_DIR / filename
            cleaned[key].to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"  [SAUVEGARDE] {filename} -> {len(cleaned[key])} lignes")


# ---------------------------------------------------------------------------
# 2. Agrégation population par région
# ---------------------------------------------------------------------------

def build_population_territories(pop_df: pd.DataFrame) -> pd.DataFrame:
    df = pop_df[pop_df["sexe"] == "Total"].copy()

    REGIONS_TOGO = {
        "SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME", "GRAND LOME",
        "GOLFE", "LOME"
    }

    national = df[df["decoupage_administratif"].str.upper() == "TOGO"].copy()
    regional = df[df["geo_normalisee"].isin(REGIONS_TOGO)].copy()

    sous_niveaux = df[
        ~df["geo_normalisee"].isin({"TOGO"} | REGIONS_TOGO)
    ].copy()

    national["niveau_administratif"] = "national"
    regional["niveau_administratif"] = "region"
    sous_niveaux["niveau_administratif"] = "sous_region"

    result = pd.concat([national, regional, sous_niveaux], ignore_index=True)
    print(f"  population_territories : {len(result)} lignes "
          f"(national={len(national)}, regions={len(regional)}, sous-niveaux={len(sous_niveaux)})")
    return result


# ---------------------------------------------------------------------------
# 3. Agrégation Mobile Money par région
# ---------------------------------------------------------------------------

def build_mobile_money_territories(mm_df: pd.DataFrame):
    by_region = mm_df.groupby("region_normalisee", dropna=False).size().reset_index(name="nb_agents_mobile_money")
    by_region["niveau"] = "region"
    by_region = by_region.rename(columns={"region_normalisee": "territoire"})

    by_pref = mm_df.groupby(
        ["region_normalisee", "prefecture_normalisee"], dropna=False
    ).size().reset_index(name="nb_agents_mobile_money")
    by_pref["niveau"] = "prefecture"
    by_pref = by_pref.rename(columns={
        "region_normalisee": "region",
        "prefecture_normalisee": "territoire"
    })

    by_commune = mm_df.groupby(
        ["region_normalisee", "prefecture_normalisee", "commune_normalisee"], dropna=False
    ).size().reset_index(name="nb_agents_mobile_money")
    by_commune["niveau"] = "commune"
    by_commune = by_commune.rename(columns={
        "region_normalisee": "region",
        "prefecture_normalisee": "prefecture",
        "commune_normalisee": "territoire"
    })

    print(f"  mobile_money_territories : regions={len(by_region)}, prefectures={len(by_pref)}, communes={len(by_commune)}")
    return by_region, by_pref, by_commune


# ---------------------------------------------------------------------------
# 4. Agrégation Établissements Financiers par région
# ---------------------------------------------------------------------------

def build_finance_territories(fin_df: pd.DataFrame):
    by_region = fin_df.groupby("region_normalisee", dropna=False).size().reset_index(
        name="nb_etablissements"
    )
    by_region["niveau"] = "region"
    by_region = by_region.rename(columns={"region_normalisee": "territoire"})

    by_cat_region = fin_df.groupby(
        ["region_normalisee", "activite_categorie"], dropna=False
    ).size().reset_index(name="nb_etablissements")

    by_pref = fin_df.groupby(
        ["region_normalisee", "prefecture_normalisee"], dropna=False
    ).size().reset_index(name="nb_etablissements")
    by_pref["niveau"] = "prefecture"
    by_pref = by_pref.rename(columns={
        "region_normalisee": "region",
        "prefecture_normalisee": "territoire"
    })

    print(f"  finance_territories : regions={len(by_region)}, catxregion={len(by_cat_region)}, prefectures={len(by_pref)}")
    return by_region, by_cat_region, by_pref


# ---------------------------------------------------------------------------
# 5. Table territorial_access
# ---------------------------------------------------------------------------

def build_territorial_access(
    pop_territories: pd.DataFrame,
    mm_by_region: pd.DataFrame,
    fin_by_region: pd.DataFrame,
) -> pd.DataFrame:
    REGIONS_TOGO = {
        "SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME", "GRAND LOME",
        "GOLFE", "LOME"
    }
    pop_reg = pop_territories[
        (pop_territories["niveau_administratif"] == "region") &
        (pop_territories["sexe"] == "Total")
    ][["geo_normalisee", "valeur"]].copy()
    pop_reg = pop_reg.rename(columns={"geo_normalisee": "region", "valeur": "population_2022"})

    n_pop = len(pop_reg)

    mm_reg = mm_by_region[["territoire", "nb_agents_mobile_money"]].copy()
    mm_reg = mm_reg.rename(columns={"territoire": "region"})
    n_mm = len(mm_reg)

    fin_reg = fin_by_region[["territoire", "nb_etablissements"]].copy()
    fin_reg = fin_reg.rename(columns={"territoire": "territoire_fin"})
    n_fin = len(fin_reg)

    merged = pd.merge(pop_reg, mm_reg, on="region", how="outer")
    n_after_mm = len(merged)
    mm_match = merged["population_2022"].notna().sum()
    match_rate_mm = mm_match / max(n_pop, n_mm) * 100 if max(n_pop, n_mm) > 0 else 0

    unmatched_mm = merged[merged["population_2022"].isna() | merged["nb_agents_mobile_money"].isna()]
    issues_mm = ""
    if len(unmatched_mm) > 0:
        issues_mm = f"Regions sans correspondance : {unmatched_mm['region'].tolist()}"

    _log_join(
        "population (2022) x mobile_money (2024) - niveau region",
        n_pop, n_mm, n_after_mm, match_rate_mm, issues_mm
    )

    fin_reg2 = fin_by_region[["territoire", "nb_etablissements"]].copy()
    fin_reg2 = fin_reg2.rename(columns={"territoire": "region"})
    merged = pd.merge(merged, fin_reg2, on="region", how="outer")
    n_after_fin = len(merged)
    fin_match = merged["population_2022"].notna().sum()
    match_rate_fin = fin_match / max(n_pop, n_fin) * 100 if max(n_pop, n_fin) > 0 else 0

    unmatched_fin = merged[merged["nb_etablissements"].isna()]
    issues_fin = ""
    if len(unmatched_fin) > 0:
        issues_fin = f"Regions sans nb_etablissements : {unmatched_fin['region'].tolist()}"

    _log_join(
        "merged x finance (2025) - niveau region",
        n_after_mm, n_fin, n_after_fin, match_rate_fin, issues_fin
    )

    pop = merged["population_2022"]
    agents = merged["nb_agents_mobile_money"]
    etab = merged["nb_etablissements"]

    merged["agents_pour_10000_hab"] = np.where(
        pop.notna() & agents.notna() & (pop > 0),
        (agents / pop * 10000).round(2),
        np.nan
    )
    merged["habitants_par_agent"] = np.where(
        pop.notna() & agents.notna() & (agents > 0),
        (pop / agents).round(1),
        np.nan
    )
    merged["etab_pour_10000_hab"] = np.where(
        pop.notna() & etab.notna() & (pop > 0),
        (etab / pop * 10000).round(2),
        np.nan
    )
    merged["habitants_par_etab"] = np.where(
        pop.notna() & etab.notna() & (etab > 0),
        (pop / etab).round(1),
        np.nan
    )

    merged["note_temporelle"] = (
        "Population 2022 | Agents Mobile Money collectes 2024-12-19 | "
        "Etablissements financiers collectes 2025-01-08. "
        "Les ratios croisent des millesimes differents - meintenir precaution."
    )

    print(f"  territorial_access : {len(merged)} lignes (niveau region)")
    return merged


# ---------------------------------------------------------------------------
# Contrôles de cohérence avant/après
# ---------------------------------------------------------------------------

def run_quality_checks(raw_datasets: dict, cleaned: dict, territorial: pd.DataFrame) -> list[str]:
    checks = []

    for name in raw_datasets:
        if name in cleaned:
            n_raw = len(raw_datasets[name])
            n_clean = len(cleaned[name])
            diff = n_raw - n_clean
            checks.append(f"  [OK] {name:20s} : {n_raw} -> {n_clean} ({diff:+d} lignes supprimees)")

    if "population" in cleaned:
        pop_total_raw = pd.to_numeric(raw_datasets["population"]["Value"], errors="coerce").sum()
        pop_total_clean = cleaned["population"]["valeur"].sum()
        diff_pop = abs(pop_total_raw - pop_total_clean)
        checks.append(f"  [OK] Population total brut  : {pop_total_raw:,.0f}")
        checks.append(f"  [OK] Population total propre: {pop_total_clean:,.0f}")
        checks.append(f"  [OK] Difference            : {diff_pop:,.0f}")

    if "mobile_money" in cleaned:
        n_agents_raw = len(raw_datasets["mobile_money"])
        n_agents_clean = len(cleaned["mobile_money"])
        checks.append(f"  [OK] Agents Mobile Money   : {n_agents_raw} -> {n_agents_clean}")

    if "finance" in cleaned:
        n_fin_raw = len(raw_datasets["finance"])
        n_fin_clean = len(cleaned["finance"])
        checks.append(f"  [OK] Etablissements finance : {n_fin_raw} -> {n_fin_clean}")

    if "finance" in cleaned and "activite_categorie" in cleaned["finance"].columns:
        cats = cleaned["finance"]["activite_categorie"].value_counts(dropna=False)
        checks.append(f"  [OK] Categories finance apres nettoyage : {cats.to_dict()}")

    if "telecom" in cleaned:
        arpu_rows = cleaned["telecom"][
            cleaned["telecom"]["indicateur"].str.contains("ARPU", case=False, na=False)
        ]
        checks.append(f"  [OK] Lignes ARPU meinteneues : {len(arpu_rows)} (anomalie signalee, non meinteneue)")

    if "internet_users" in cleaned:
        row_2023 = cleaned["internet_users"][cleaned["internet_users"]["annee"] == 2023]
        val_2023 = row_2023["valeur"].values[0] if len(row_2023) > 0 else "ligne absente"
        checks.append(f"  [OK] Internet_users 2023 = {val_2023} (attendu: NaN)")

    if territorial is not None:
        n_nan_agents = territorial["agents_pour_10000_hab"].isna().sum()
        checks.append(f"  [OK] territorial_access : {n_nan_agents} regions sans ratio agents calculable")

    return checks


def get_join_log() -> list[dict]:
    return JOIN_LOG


def run_transforms(cleaned: dict[str, pd.DataFrame], raw_datasets: dict) -> dict:
    print("\n--- Sauvegarde datasets nettoyes ---")
    save_cleaned(cleaned)

    print("\n--- Construction population_territories ---")
    pop_territories = build_population_territories(cleaned["population"])
    pop_territories.to_csv(PROCESSED_DIR / "population_territories.csv", index=False, encoding="utf-8-sig")

    print("\n--- Construction mobile_money_territories ---")
    mm_by_region, mm_by_pref, mm_by_commune = build_mobile_money_territories(cleaned["mobile_money"])
    mm_by_region.to_csv(PROCESSED_DIR / "mobile_money_territories_region.csv", index=False, encoding="utf-8-sig")
    mm_by_pref.to_csv(PROCESSED_DIR / "mobile_money_territories_prefecture.csv", index=False, encoding="utf-8-sig")
    mm_by_commune.to_csv(PROCESSED_DIR / "mobile_money_territories_commune.csv", index=False, encoding="utf-8-sig")

    print("\n--- Construction finance_territories ---")
    fin_by_region, fin_by_cat_region, fin_by_pref = build_finance_territories(cleaned["finance"])
    fin_by_region.to_csv(PROCESSED_DIR / "finance_territories_region.csv", index=False, encoding="utf-8-sig")
    fin_by_cat_region.to_csv(PROCESSED_DIR / "finance_territories_cat_region.csv", index=False, encoding="utf-8-sig")
    fin_by_pref.to_csv(PROCESSED_DIR / "finance_territories_prefecture.csv", index=False, encoding="utf-8-sig")

    print("\n--- Construction territorial_access ---")
    territorial = build_territorial_access(pop_territories, mm_by_region, fin_by_region)
    territorial.to_csv(OUTPUT_DIR / "territorial_access.csv", index=False, encoding="utf-8-sig")

    print("\n--- Controles de coherence ---")
    checks = run_quality_checks(raw_datasets, cleaned, territorial)
    for c in checks:
        print(c)

    return {
        "pop_territories": pop_territories,
        "mm_by_region": mm_by_region,
        "mm_by_pref": mm_by_pref,
        "mm_by_commune": mm_by_commune,
        "fin_by_region": fin_by_region,
        "fin_by_cat_region": fin_by_cat_region,
        "fin_by_pref": fin_by_pref,
        "territorial": territorial,
        "quality_checks": checks,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from load_data import load_all
    from clean_data import clean_all
    dfs = load_all()
    cleaned = clean_all(dfs)
    run_transforms(cleaned, dfs)
