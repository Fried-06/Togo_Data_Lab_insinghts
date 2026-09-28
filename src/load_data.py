"""
load_data.py
============
Chargement des datasets bruts depuis data/raw/.

Aucune transformation n'est effectuée ici, sauf la détection de l'encodage.
Les fichiers sources restent intacts.
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

# Mapping nom logique → fichier physique
FILES = {
    "population": "observationdata-kwwolwb.csv",
    "telecom": "observationdata-mesqyx.csv",
    "internet_tech": "observationdata-cxnvmoc.csv",
    "internet_users": "individus-utilisant-internet-de-la-population-.csv",
    "mobile_money": "file-agents-mobile-money-19-12-2024-16-55-32.csv",
    "finance": "file-finance-etablissements-08-01-2025-17-49-30.csv",
}


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Lit un CSV en essayant successivement UTF-8, puis latin-1."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=encoding, **kwargs)
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Impossible de lire {path} avec les encodages testés.")


def load_all() -> dict[str, pd.DataFrame]:
    """
    Charge tous les datasets bruts.

    Retourne un dictionnaire :
        {
            'population': DataFrame,
            'telecom':    DataFrame,
            ...
        }
    """
    datasets: dict[str, pd.DataFrame] = {}
    for name, filename in FILES.items():
        path = RAW_DIR / filename
        if not path.exists():
            print(f"[AVERTISSEMENT] Fichier introuvable : {path}")
            continue
        df = _read_csv(path)
        datasets[name] = df
        print(f"[OK] {name:20s} -> {len(df):>6} lignes x {len(df.columns)} colonnes  [{filename}]")
    return datasets


if __name__ == "__main__":
    dfs = load_all()
