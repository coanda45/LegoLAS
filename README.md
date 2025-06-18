# 🏗️ LEGOLAS
LegoLAS (LEGO: Locate And Sum) est un projet permettant aux utilisateurs d'identifier des pièces LEGO à partir d'une photo et d'obtenir la liste des sets réalisables avec ces pièces. Il aide également à déterminer les pièces manquantes.


## 🎯 Objectif du projet

LegoLAS repose sur des techniques avancées de reconnaissance d'image et d'analyse des bases de données pour :

- 📸 Analyser une photo des pièces LEGO prises par l'utilisateur:
    - ✂️ Segmenter l'image (c'est-à-dire identifier les zones de l'image présentant une pièce LEGO) à l'aide de trois modèles proposés, à choisir par l'utilisateur.
    - 🔍 Classifier les pièces via l’API Brickognize (c'est-à-dire identifier les pièces LEGO et leur couleur correspondantes).
- 🏗️ Rechercher les sets compatibles pouvant être construits avec toutes ou partie de ces pièces. Les 10 sets présentant le pourcentage de pièces disponibles sont présentés, que l'on tienne compte (ou non) des couleurs des pièces disponibles.
- 🧩 Lister les pièces manquantes nécessaires pour compléter un set ainsi que les pièces en trop.


## 🚀 Fonctionnalités

  ### ✂️ Segmentation d’image
  LegoLAS intègre trois modèles à choisir par l'utilisateur pour une segmentation précise des pièces LEGO :

  un modèle "rapide" mais susceptible de ne pas reconnaître l'ensemble des pièces (utilisant le modèle disponible à l'adresse suivante : https://universe.roboflow.com/test-lego-brick-annotatie/lego_object_detection-5lfzr/) : de l'ordre de quelques secondes à dizaines de secondes selon le nombre de pièces sur la photo ;
  un modèle un peu moins "rapide" mais susceptible de reconnaître davantage des pièces (utilisant le modèle disponible à l'adresse suivante : https://universe.roboflow.com/vcomtask3/lego-brick-detector-xvqkq) : de l'ordre de quelques dizaines de secondes selon le nombre de pièces sur la photo ;
  un modèle "lent' mais qui devrait laisser pas ou peu de pièces non segmentées (utilisant le modèle Segment Anything développé par Meta : https://segment-anything.com/) : de l'ordre de la dizaine de secondes à la minutes selon le nombre de pièces sur la photo."
  Ces trois modèles permettent :
  - Détection des contours et formes des pièces LEGO.
  - Séparation des pièces superposées ou partiellement visibles.
  - Extraction individuelle des éléments pour une meilleure classification.

  ### 🔍 Classification
  Les pièces segmentées sont classées via Brickognize, une API basée sur les réseaux de neurones convolutifs (CNNs), précision du modèle : 91,33 % en conditions réelles, 98,7 % en environnement contrôlé.
  - Attribution des références Brinklink en fonction de leur forme.
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
  - API Rebrickable pour récupération des détails complémentaires
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
