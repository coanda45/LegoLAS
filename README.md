# 🏗️ LEGOLAS
LegoLAS (LEGO: Locate And Sum) est un projet permettant aux utilisateurs d'identifier des pièces LEGO à partir d'une photo et d'obtenir la liste des sets réalisables avec ces pièces. Il aide également à déterminer les pièces manquantes


## 🎯 Objectif du projet

LegoLAS repose sur des techniques avancées de reconnaissance d'image et d'analyse des bases de données pour :

- 📸 Analyser une photo des pièces LEGO prises par l'utilisateur:
    - ✂️ Segmenter l'image avec le modèle Segment Anything Model (SAM) pour séparer chaque pièce
    - 🔍 Classifier les pièces via l’API Brickognize.
- 🏗️ Rechercher les sets compatibles pouvant être construits avec ces pièces.
- 🧩 Lister les pièces manquantes nécessaires pour compléter un set.


## 🚀 Fonctionnalités

  ### ✂️ Segmentation d’image
  LegoLAS intègre Segment Anything Model (SAM) pour une segmentation précise des pièces LEGO :
  - Détection des contours et formes des pièces LEGO.
  - Séparation des pièces superposées ou partiellement visibles.
  - Extraction individuelle des éléments pour une meilleure classification.

  ### 🔍 Classification
  Les pièces segmentées sont classées via Brickognize, une API basée sur les réseaux de neurones convolutifs (CNNs), précision du modèle : 91,33 % en conditions réelles, 98,7 % en environnement contrôlé.
  - Attribution des références Brinkink en fonction de leur forme.
  - Comparaison avec une base de données Rebrickable (API) pour obtenir les identifiants Rebrickable.
  - Obtention de la couleur de la pièce par ⚠️ "AJOUTER LA TECHNIQUE UTILISE"⚠️

  ### 🏗️ Recherche des sets réalisables
  - Extraction des sets LEGO/Rebrickable compatibles avec les pièces trouvées.
  - Tri des résultats selon le taux de complétion (exemple : Vous avez 80 % des pièces nécessaires)
  - Suggestion des sets les plus proches de l'inventaire utilisateur.
  - Comparaison avec les sets pour détecter les pièces absentes et génération de la liste des pièces absentes


## 📦 Technologies utilisées

  - Python pour le traitement des données.
  - Pandas pour l’analyse et la gestion des données.
  - Segment Anything Model (SAM) pour la segmentation des pièces LEGO.
  - API Brickognize pour la classification des pièces LEGO.
  - API Rebrickable pour complétude des détails complémentaire.
  - Exploitation des CSV (DataBase Rebrickable) pour proposition des sets.


## ⚙️ Installation et configuration

#### Cloner le projet

```bash
git clone https://github.com/nicolas-corbet/LegoLAS.git
cd LegoLAS
```
#### Installer les dépendances

```bash
pip install -r requirements.txt
```

#### Configurer l’accès à Rebrickable et Brickognize
- Créez/complétez le fichier .env et ajoutez vos clés API :
```bash
KEY_USER = your_api_key_rebrickable

A COMPLETER
```

# API
Document main API endpoints here

# Setup instructions
Document here for users who want to setup the package locally

# Usage
Document main functionalities of the package here
