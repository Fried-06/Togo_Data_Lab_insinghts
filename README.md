# TOGO DIGITAL INSIGHT
### Observatoire interactif de l'inclusion numérique et financière au Togo

Plateforme institutionnelle d'intelligence territoriale et d'aide à la décision publique, développée pour analyser l'évolution de la connectivité Internet, la transition technologique télécoms et l'accès aux services financiers (Banques, Microfinances et Mobile Money) sur l'ensemble du territoire togolais.

---

## 1. Architecture et Principes Directeurs

Le produit applique rigoureusement la méthodologie :
**PROBLÈME $\rightarrow$ PREUVE $\rightarrow$ TERRITOIRE $\rightarrow$ EXPLICATION $\rightarrow$ PISTE D'ACTION**

* **Aucune donnée inventée** : Chaque indicateur et ratio découle des recensements officiels (RGPH-5 INSEED 2022) et des données déclaratives (ARCEP, Banque Mondiale / ITU, cartographie terrain).
* **Système de couleur sémantique strict** :
  * 🟢 **Vert** : Favorable / Progression / Accès solide
  * 🟡 **Jaune** : Situation intermédiaire / Vigilance
  * 🔴 **Rouge** : Déficit relatif / Sous-densité
  * 🔵 **Bleu** : Télécommunications / Connectivité Internet
  * 🟣 **Violet** : Finance numérique / Mobile Money
  * ⚪ **Gris** : Contexte / Référence
* **Design sobre et institutionnel** : Typographie Inter, pas d'effets superflus ni d'emojis, lisibilité et rigueur statistique maximales.

---

## 2. Structure des 7 Pages de l'Observatoire

1. **Vue d'ensemble (`/`)** : Synthèse exécutive, 4 KPI nationaux certifiés, courbe de trajectoire historique et observations majeures.
2. **Internet (`/internet`)** : Évolution de l'adoption avec sélecteur d'indicateur et distinction méthodologique entre taux d'utilisation individuel et taux de pénétration des abonnements.
3. **Connectivité (`/connectivity`)** : Transition technologique 2G $\rightarrow$ 3G $\rightarrow$ 4G, émergence du FTTH fixe et dynamique concurrentielle des parts de marché (Togocom vs Moov).
4. **Territoires (`/territories`)** : Carte choroplèthe interactive des 5 régions officielles (Savanes, Kara, Centrale, Plateaux, Maritime), ratios pour 10 000 habitants et profil régional dynamique.
5. **Finance (`/finance`)** : Analyse comparée des réseaux physiques (Banques, Microfinances, Assurances, Mutuelles) face au maillage de proximité des agents Mobile Money.
6. **Diagnostic (`/diagnostic`)** : Matrice des disparités et classification objective fondée sur les écarts relatifs à la moyenne nationale pondérée.
7. **Recommandations (`/recommendations`)** : 4 axes d'implications analytiques structurés en *Observation $\rightarrow$ Donnée $\rightarrow$ Interprétation $\rightarrow$ Piste d'action*.

---

## 3. Installation et Démarrage Local

### Prérequis
* Python 3.10 ou supérieur

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancement du tableau de bord
```bash
python app.py
```
L'observatoire est alors immédiatement accessible dans votre navigateur à l'adresse :
👉 **http://127.0.0.1:8050/**

---

## 4. Déploiement en Production

Le fichier `app.py` expose l'objet WSGI standard `server = app.server`, compatible avec tous les hébergeurs cloud Python (Gunicorn, Render, Heroku, AWS Elastic Beanstalk, etc.) :

```bash
gunicorn app:server --bind 0.0.0.0:8050
```

---

## 5. Sources Primaires
* **INSEED Togo** : Recensement Général de la Population et de l'Habitat (RGPH-5, 2022).
* **ARCEP Togo** : Données des observatoires annuels du marché des télécommunications (2013-2019).
* **Banque Mondiale & UIT (ITU)** : World Development Indicators (1960-2023).
* **Cartographie terrain Mobile Money** : Relevé géolocalisé (décembre 2024).
* **Répertoire des établissements financiers** : Données de localisation (janvier 2025).
