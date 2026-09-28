"""
main.py
=======
Script principal d'exécution reproductible du pipeline TogoAI Labs.

Étapes :
    1. Chargement des datasets bruts (load_data.py)
    2. Diagnostic et analyse exploratoire (validate_data.py)
    3. Nettoyage et normalisation (clean_data.py)
    4. Transformation et construction des datasets analytiques (transform_data.py)
    5. Génération automatique d'un résumé de synthèse

Exécution :
    python src/main.py
"""

import sys
from pathlib import Path

# Inclusion du répertoire src dans le PYTHONPATH
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from load_data import load_all
from validate_data import run_diagnostics
from clean_data import clean_all, get_quality_log
from transform_data import run_transforms, get_join_log


def main():
    print("=" * 80)
    print("  TOGOAI LABS — PIPELINE DE PRÉPARATION & NETTOYAGE DES DATASETS")
    print("=" * 80)

    # 1. Chargement
    print("\n>>> ÉTAPE 1 : Chargement des datasets bruts (data/raw/)")
    raw_dfs = load_all()

    # 2. Diagnostic exploratoire
    print("\n>>> ÉTAPE 2 : Diagnostic exploratoire automatique")
    reports = run_diagnostics(raw_dfs)

    # 3. Nettoyage
    print("\n>>> ÉTAPE 3 : Nettoyage et normalisation")
    cleaned_dfs = clean_all(raw_dfs)
    quality_log = get_quality_log()

    # 4. Transformations et tables analytiques
    print("\n>>> ÉTAPE 4 : Transformations & tables analytiques")
    results = run_transforms(cleaned_dfs, raw_dfs)
    join_log = get_join_log()

    # 5. Résumé de synthèse
    print("\n" + "=" * 80)
    print("  RÉSUMÉ DU TRAITEMENT COMPLÉTÉ")
    print("=" * 80)
    print(f"  - Datasets bruts analysés   : {len(raw_dfs)}")
    print(f"  - Transformations enregistrées : {len(quality_log)}")
    print(f"  - Jointures documentées        : {len(join_log)}")
    print(f"  - Fichiers générés dans data/processed/ et data/output/")
    print("\n  Le pipeline s'est exécuté avec succès.")
    print("=" * 80)


if __name__ == "__main__":
    main()
