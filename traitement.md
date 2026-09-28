# Documentation du Traitement et Nettoyage des Données — TogoAI Labs

Ce document détaille l'ensemble du travail de préparation, de nettoyage, de validation et de structuration des données réalisé dans le cadre du projet TogoAI Labs sur la connectivité Internet et l'inclusion financière numérique au Togo.

---

## 1. Objectif

L'objectif principal de ce traitement est de produire des datasets propres, nettoyés, validés et directement exploitables pour construire ultérieurement un dashboard analytique et un rapport stratégique PowerPoint.

Il s'agit spécifiquement de :
* Uniformiser et structurer les données démographiques, financières et de télécommunications.
* Documenter et résoudre les anomalies identifiées sans détruire l'information source.
* Établir les tables d'agrégation territoriale (régionale et sous-régionale) permettant de calculer des indicateurs de densité et d'accès aux services financiers.
* Conserver la traçabilité intégrale entre les données brutes (`data/raw/`) et les données transformées (`data/processed/` et `data/output/`).

---

## 2. Datasets utilisés

Le projet s'appuie sur 6 fichiers CSV bruts conservés intacts dans `data/raw/` :

| Nom logique | Fichier source (`data/raw/`) | Rôle & Contenu principal | Lignes brutes | Colonnes brutes | Période couverte |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `population` | `observationdata-kwwolwb.csv` | Population résidente par découpage administratif et par sexe | 759 | 6 | 2022 |
| `telecom` | `observationdata-mesqyx.csv` | Abonnés fixe/mobile, teledensité, CA, investissements, parts de marché, ARPU | 70 | 4 | 2013 – 2019 |
| `internet_tech` | `observationdata-cxnvmoc.csv` | Abonnés par technologie (3G, 4G, ADSL, FTTH, Wimax, etc.) et taux de pénétration | 160 | 4 | 2013 – 2019 |
| `internet_users` | `individus-utilisant-internet-de-la-population-.csv` | Indicateur Banque Mondiale : *Individuals using the Internet (% of population)* | 64 | 8 | 1960 – 2023 |
| `mobile_money` | `file-agents-mobile-money-19-12-2024-16-55-32.csv` | Points de présence/agents Mobile Money géolocalisés | 19 788 | 7 | 2024-12-19 |
| `finance` | `file-finance-etablissements-08-01-2025-17-49-30.csv` | Établissements financiers (Banque, Micro-Finance, Assurance, Mutuelle) | 738 | 13 | 2025-01-08 |

---

## 3. Problèmes détectés

Lors du diagnostic exploratoire automatique (`src/validate_data.py`), plusieurs anomalies ont été recensées :

1. **Faute de frappe catégorielle (`finance`)** :
   * Une ligne enregistrait l'établissement en sous-catégorie `Micro-Finace` au lieu de `Micro-Finance`.
2. **Anomalie d'échelle ARPU (`telecom`)** :
   * L'indicateur `ARPU segment mobile GSM` présente des valeurs de l'ordre de $2.4 \times 10^{13}$ à $3.3 \times 10^{13}$ FCFA.
3. **Incohérence d'unité de pénétration (`internet_tech`)** :
   * `Taux de pénétration Internet (Toutes technologies) (%)` et `Taux de pénétration Internet haut débit (%)` ont la valeur `Nombre` dans la colonne `Unit`, alors que leurs valeurs sont clairement des pourcentages (ex: 5.24 à 49.55).
4. **Hétérogénéité des noms géographiques** :
   * Différences de casse, préfixes/suffixes et espaces parasites dans les noms de régions, préfectures et communes entre les datasets `population`, `mobile_money` et `finance`.
5. **Préfixe ambigu `T ` (`internet_tech`)** :
   * Certains indicateurs commencent par `T ` (ex: `T abonnés Internet...`), abréviation de *Total*.
6. **Valeurs manquantes vs Zéros** :
   * Dans `internet_users`, la valeur pour 2023 est absente (`NaN`).
   * Dans `internet_tech`, les technologies récentes (ex: 4G avant 2018 ou FTTH) possèdent des `0` explicites qui traduisent une indisponibilité commerciale et non une absence de mesure.
7. **Décalages temporels (Millésimes)** :
   * `population` est mesurée en 2022.
   * `mobile_money` est daté du 19/12/2024.
   * `finance` est daté du 08/01/2025.
   * `telecom` / `internet_tech` s'arrêtent à 2019.

---

## 4. Corrections effectuées

Toutes les transformations réalisées sont motivées et tracées dans le journal qualité :

```text
1. Problème     : Faute de frappe 'Micro-Finace' dans le dataset finance
   Décision     : Remplacer 'Micro-Finace' par 'Micro-Finance'
   Transformation: clean['activite_categorie'].replace('Micro-Finace', 'Micro-Finance')
   Justification: Erreur de saisie évidente. La colonne originale est conservée sous 'activite_categorie_orig'.

2. Problème     : Espaces parasites et casse incohérente dans les noms géographiques
   Décision     : Créer des colonnes géographiques normalisées (*_normalisee)
   Transformation: Application de str.strip().str.upper() sur les champs de région/préfecture/commune
   Justification: Permet des jointures exactes inter-datasets sans détruire les libellés sources.

3. Problème     : Colonnes avec accents et tirets dans les entêtes du dataset population
   Décision     : Renommer les entêtes en snake_case sans accent
   Transformation: decoupage-administratif -> decoupage_administratif, Date -> annee, Value -> valeur
   Justification: Normalisation standard pour la manipulation Python/SQL.

4. Problème     : Unité 'Nombre' indiquée pour le taux de pénétration Internet (en %)
   Décision     : Ajouter une colonne 'unit_corrigee' = 'Pourcentage'
   Transformation: Attribution explicite de 'Pourcentage' pour les indicateurs de taux de pénétration
   Justification: La donnée brute 'Unit' est conservée, mais 'unit_corrigee' élimine toute ambiguïté.

5. Problème     : Préfixe 'T ' ambigu dans le dataset internet_tech
   Décision     : Ajouter une colonne 'indicateur_propre' étendant 'T ' en 'Total '
   Transformation: Regex re.sub(r"^T\s+", "Total ", label)
   Justification: Améliore la lisibilité des graphiques et des agrégations futures.

6. Problème     : Coordonnées géographiques encapsulées dans une chaîne 'POINT (lon lat)'
   Décision     : Extraire les colonnes numériques 'longitude' et 'latitude'
   Transformation: Regex de parsing sur la colonne 'geometry'
   Justification: Facilite le filtrage spatial et l'affichage SIG ultérieur.
```

---

## 5. Bibliothèques utilisées

Le traitement repose exclusivement sur la bibliothèque standard et les librairies fondamentales Data Science de Python :

* `pandas` : Chargement, filtrage, nettoyage, normalisation, agrégations (`groupby`), jointures (`merge`) et exportation en CSV.
  * `pd.read_csv()` : Lecture des fichiers bruts avec détection d'encodage (UTF-8, Latin-1).
  * `df.info()`, `df.describe()`, `df.isna()`, `df.duplicated()` : Diagnostic exploratoire.
  * `df.rename()`, `df.astype()`, `df.replace()` : Nettoyage et typage.
  * `df.groupby()`, `df.merge()` : Agrégation territoriale et calcul des indicateurs croisés.
* `numpy` : Utilisation de `np.where` et `np.nan` pour l'évaluation conditionnelle sécurisée des indicateurs ratio.
* `pathlib.Path` : Gestion propre, portable et multiplateforme des chemins de fichiers.
* `re` : Expressions régulières pour le parsing des géométries et le nettoyage des préfixes d'indicateurs.

---

## 6. Explication du code

Le code du pipeline est structuré de façon modulaire et reproductible dans le dossier `src/` :

* `src/load_data.py` :
  Charge l'ensemble des datasets bruts depuis `data/raw/` en testant plusieurs encodages. Conserve les DataFrames intacts en mémoire dans un dictionnaire.
* `src/validate_data.py` :
  Parcourt chaque dataset et génère un diagnostic exploratoire automatique (dimensions, types, valeurs nulles, doublons, plages numériques, modalités et anomalies).
* `src/clean_data.py` :
  Applique les règles de nettoyage spécifique pour chaque dataset. Conserve les valeurs originales tout en ajoutant des colonnes normalisées et enregistre chaque action dans le journal `QUALITY_LOG`.
* `src/transform_data.py` :
  Sauvegarde les versions nettoyées dans `data/processed/`, construit les agrégations territoriales (régions, préfectures, communes) et assemble la table finale `territorial_access.csv` dans `data/output/`.
* `src/main.py` :
  Point d'entrée unique exécutant séquentiellement l'ensemble de la chaîne de traitement.

---

## 7. Jointures

Le raccordement des données s'effectue au niveau **RÉGION** pour construire la table analytique `data/output/territorial_access.csv` :

1. **Population $\times$ Mobile Money** :
   * **Clé de jointure** : `region` (nom de région normalisé).
   * **Lignes gauche (Population)** : 6 (Savanes, Kara, Centrale, Plateaux, Maritime, Golfe).
   * **Lignes droite (Mobile Money)** : 5 (les 5 régions administratives ; Golfe étant rattaché à Maritime).
   * **Taux de correspondance** : 100% sur les 5 régions majeures.
   * **Résultat** : Les 5 régions disposent d'un ratio complet. Golfe dispose de la valeur population et garde des valeurs `NaN` pour les agents (qui sont comptabilisés dans Maritime).

2. **Population / Mobile Money $\times$ Établissements Financiers** :
   * **Clé de jointure** : `region`.
   * **Taux de correspondance** : 100% sur les régions administratives.

---

## 8. Indicateurs calculés

Pour étudier l'accès territorial aux services financiers, les indicateurs suivants sont calculés dans `territorial_access.csv` :

$$\text{Agents pour 10 000 habitants} = \frac{\text{Nombre d'agents Mobile Money}}{\text{Population}} \times 10\,000$$

$$\text{Habitants par agent Mobile Money} = \frac{\text{Population}}{\text{Nombre d'agents Mobile Money}}$$

$$\text{Établissements pour 10 000 habitants} = \frac{\text{Nombre d'établissements financiers}}{\text{Population}} \times 10\,000$$

$$\text{Habitants par établissement financier} = \frac{\text{Population}}{\text{Nombre d'établissements financiers}}$$

*Note* : Un calcul n'est exécuté que si la population et le nombre d'agents/établissements sont tous deux disponibles et supérieurs à 0. Dans le cas contraire, la valeur `NaN` est strictement préservée.

---

## 9. Anomalies conservées

Les anomalies suivantes n'ont **pas** été modifiées arbitrairement et ont été volontairement conservées dans les jeux nettoyés :

1. **ARPU Segment Mobile GSM (`telecom_clean.csv`)** :
   * **Constat** : Les valeurs tournent autour de 24 à 33 billions FCFA ($10^{13}$).
   * **Motif de conservation** : Sans confirmation de l'organisme émetteur (s'il s'agit du chiffre d'affaires global du secteur ramené ou d'une erreur d'unité en centimes/francs), toute division par $10^6$ ou $10^9$ serait une pure conjecture. Une colonne `arpu_anomalie_flag` = `True` a été ajoutée pour le signaler dans les futurs rapports.
2. **Indicateur Banque Mondiale `Individuals using the Internet` en 2023 (`internet_users_clean.csv`)** :
   * **Constat** : La valeur pour 2023 est manquante (`NaN`).
   * **Motif de conservation** : Ne pas imputer par 0 ni par la valeur de 2022. La donnée n'était pas encore publiée lors de la constitution de la table.
3. **Pénétration Internet $\times$ Utilisateurs Internet** :
   * Les deux indicateurs (`Taux de pénétration` et `Individuals using the Internet`) restent dans deux datasets séparés car leurs méthodologies et sources diffèrent (ARCEP/Ministère vs Banque Mondiale/ITU).

---

## 10. Structure finale des données

Après exécution du pipeline, l'arborescence des données s'établit comme suit :

```text
Togo_Data_Challenge/
├── data/
│   ├── raw/                               # Fichiers originaux intacts
│   │   ├── observationdata-kwwolwb.csv
│   │   ├── observationdata-mesqyx.csv
│   │   ├── observationdata-cxnvmoc.csv
│   │   ├── individus-utilisant-internet-de-la-population-.csv
│   │   ├── file-agents-mobile-money-19-12-2024-16-55-32.csv
│   │   └── file-finance-etablissements-08-01-2025-17-49-30.csv
│   │
│   ├── processed/                         # Datasets nettoyés et agrégations
│   │   ├── population_clean.csv
│   │   ├── telecom_clean.csv
│   │   ├── internet_tech_clean.csv
│   │   ├── internet_users_clean.csv
│   │   ├── mobile_money_clean.csv
│   │   ├── finance_clean.csv
│   │   ├── population_territories.csv
│   │   ├── mobile_money_territories_region.csv
│   │   ├── mobile_money_territories_prefecture.csv
│   │   ├── mobile_money_territories_commune.csv
│   │   ├── finance_territories_region.csv
│   │   ├── finance_territories_cat_region.csv
│   │   └── finance_territories_prefecture.csv
│   │
│   └── output/                            # Table analytique finale
│       └── territorial_access.csv
│
├── src/                                   # Scripts Python du pipeline
│   ├── load_data.py
│   ├── validate_data.py
│   ├── clean_data.py
│   ├── transform_data.py
│   └── main.py
│
├── requirements.txt                       # Dépendances Python
└── traitement.md                          # Présente documentation
```

---

## 11. Reproduction du traitement

Pour reproduire intégralement la préparation des données depuis l'état brut :

1. S'assurer d'avoir Python 3.10+ installé.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Exécuter le pipeline principal :
   ```bash
   python src/main.py
   ```
