A réaliser après obtention de la classification (dataframe avec liste id)

## 1 - Transformer id BRICKLINK en id REBRIKABLE:

fonction export_bricklink_to_rebrickable_csv()
      Recherche les identifiants Rebrickable correspondant à une liste d'IDs Bricklink,
      et exporte les résultats dans un fichier CSV.
        Si le CSV exite pas -> le créé
        Si le CSV existe -> le complété
        Si l'id BRIKLINK non existant -> ajouter la ligne
        Si l'id BRIKLINK est existant -> quantité +1

  ⚠️ ATTENTION l'entrée est une liste [] par un recherche vers la colonne du DF


## 2 - Obtention du user_token pour les étapes suivantes :
fonction get_user_token()
      Récupère un jeton d'authentification utilisateur (user_token) depuis l'API Rebrickable.
      Cette fonction effectue une requête POST vers l'endpoint `/api/v3/users/_token/`
      en utilisant le nom d'utilisateur et le mot de passe fournis, accompagnés de la clé API.

   ⚠️L'utilisateur doit pouvoir donner ses identifiants REBRIKABLE
    USER NAME et PASSWORD -> sur streamlit creation de ses champs


## 3 - Création d'une PART LIST sur REBRICKABLE et obtenir l'ID LIST (ce qui nous interesse )
faire id_list = get_id_list(new_name_list) -> créer la list et retourne l'id_list

fonction get_id_list() qui utilise fonction create_partlist() pour retourner id_list

fonction create_partlist()
    Crée une nouvelle Part List sur REBRICKABLE avec enregistrement de l'ID list nécessaire pour la suite
    utilisation du user_token créé en amont à l'étape 2
    par defaut parametre list_type = 1 pour l'intégrer dans BUILD à la fin.


## 3 bis- au besoin supprimer list

fonction delete_partlist()

## 4 - Ajout de pièce à la LIST PART depuis le CSV obtenu(étape 1) après classification

fonction : csv_to_json_parts()

Extraction en JSON des informations nécessaire du CSV
Lit un fichier CSV et retourne une liste de dicts JSON au format attendu par l'API Rebrickable.
    Chaque dict contient les clés : 'part_num', 'color_id', 'quantity'.
    Utilise la colonne 'Rebrickable_ID_1' pour 'part_num'.

puis

fonction add_parts_to_partlist()
Ajoute plusieurs parts à une partlist Rebrickable.

## 5 Build set avec mes parts disponibles dans ma liste

Fonction do_set_with_myparts()
      Cette fonction appelle la fonction can_build_set pour retourner un df avec les information suivante :
      - % piece disponible dans ma part list pour le set demandé
      - nombre de piece manquante
