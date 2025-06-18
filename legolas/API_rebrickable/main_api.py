import requests
import requests_cache
import csv
import os
from requests.exceptions import HTTPError
import pandas as pd

REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")

cached_session = requests_cache.CachedSession('cache', expire_after=3600)


def get_rebrickable_id(bricklink_id):
    """
    Récupère l'ID Rebrickable associé à un ID BrickLink via l'API.

    Args:
        bricklink_id (str): L'identifiant BrickLink de la pièce.

    Returns:
        str: L'identifiant Rebrickable correspondant, ou None si non trouvé.
    """
    HEADERS = {"Authorization": f"key {REBRICKABLE_API_KEY}"}
    url = "https://rebrickable.com/api/v3/lego/parts/"

    params = {"bricklink_id": bricklink_id}
    response = cached_session.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    return results[0]["part_num"] if results else None


def export_bricklink_to_rebrickable_csv(bricklink_ids,
                                        output_file="list_parts.csv"):
    """
    Recherche les identifiants Rebrickable correspondant à une liste d'IDs Bricklink,
    et exporte les résultats dans un fichier CSV.

    Fonctionnalités :
    -----------------
    - Si un Bricklink ID est déjà présent dans le fichier CSV, la quantité associée est incrémentée de 1.
    - Sinon, une nouvelle ligne est ajoutée avec les informations correspondantes.
    - Les colonnes sont ordonnées comme suit : Bricklink_ID, color_id, quantity, Rebrickable_ID_1, Rebrickable_ID_2, ...
    - Le color_id est fixé à 9999, et la quantité initiale à 1 pour les nouveaux éléments.

    Format du CSV :
    ---------------
    - Bricklink_ID : identifiant d'origine (string)
    - color_id : valeur fixe (int = 9999)
    - quantity : nombre d’occurrences de cette pièce (int)
    - Rebrickable_ID_N : un ou plusieurs identifiants Rebrickable (string)

    Paramètres :
    ------------
    bricklink_ids : list[str]
        Liste des IDs Bricklink à rechercher via l'API Rebrickable.
    output_file : str, optionnel (défaut="list_parts.csv")
        Nom du fichier CSV à créer ou mettre à jour.

    Retour :
    --------
    None
        La fonction écrit ou met à jour un fichier CSV sur le disque avec les résultats obtenus.
    """
    existing_data = {}
    max_ids_per_row = 0

    # Lire les données existantes (s'il y a un fichier)
    if os.path.isfile(output_file):
        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                bl_id = row[0]
                color_id = row[1]
                quantity = int(row[2])
                rebrickable_ids = row[3:]
                existing_data[bl_id] = [bl_id, int(color_id), quantity
                                        ] + rebrickable_ids
                max_ids_per_row = max(max_ids_per_row, len(rebrickable_ids))

    for idx, bl_id in enumerate(bricklink_ids):
        print(f"[{idx+1}/{len(bricklink_ids)}] Recherche : {bl_id}")
        try:
            rebrickable_id = get_rebrickable_id(bl_id)
            rebrickable_ids = [rebrickable_id] if rebrickable_id else []
        except Exception as e:
            print(f"❌ Erreur pour {bl_id} : {e}")
            rebrickable_ids = []

        max_ids_per_row = max(max_ids_per_row, len(rebrickable_ids))

        if bl_id in existing_data:
            existing_data[bl_id][2] += 1  # Incrémenter la quantité
        else:
            existing_data[bl_id] = [bl_id, 9999, 1] + rebrickable_ids

    # Réécriture complète avec header dans l’ordre souhaité
    header = ["Bricklink_ID", "color_id", "quantity"
              ] + [f"Rebrickable_ID_{i+1}" for i in range(max_ids_per_row)]

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in existing_data.values():
            # Compléter avec des colonnes vides si nécessaire
            row += [""] * (len(header) - len(row))
            writer.writerow(row)

    print(f"\n✅ Fichier CSV mis à jour : {output_file}")


def get_user_token(user_name, password):
    """
    Récupère un jeton d'authentification utilisateur (user_token) depuis l'API Rebrickable.
    Cette fonction effectue une requête POST vers l'endpoint `/api/v3/users/_token/`
    en utilisant le nom d'utilisateur et le mot de passe fournis, accompagnés de la clé API.

    Paramètres :
    ------------
    USER_NAME : str
        Nom d'utilisateur Rebrickable.
    PASSWORD : str
        Mot de passe associé au compte Rebrickable.

    Retour :
    --------
    str or None
        Le token utilisateur (`user_token`) si la requête est réussie, sinon `None`.

    Affiche :
    ---------
    Un message d'erreur avec le code HTTP et la réponse brute si la requête échoue.

    Remarques :
    -----------
    - La variable globale `REBRICKABLE_API_KEY` doit être définie avant l'appel de cette fonction.
    - Ce token peut être utilisé ensuite pour authentifier des requêtes spécifiques à l'utilisateur (sets, lists, etc.).
    """
    URL = "https://rebrickable.com/api/v3/users/_token/"

    data = {'username': user_name, 'password': password}

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'key {REBRICKABLE_API_KEY}'
    }

    response = requests.post(URL, data=data, headers=headers)

    if response.status_code == 200:
        user_token = response.json().get('user_token')
        return user_token
    else:
        print(f"Erreur {response.status_code} : {response.text}")
        return None


def create_partlist(user_token, name_new_list, list_type=1):
    """
    Crée une nouvelle Part List.
    - name (str): nom de la liste.
    - list_type (int): 1 = utilisée pour Build, 2 = non utilisée dans Build.

    Retourne : JSON avec le détail de la liste créée.
    """
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/"
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}
    payload = {"name": name_new_list, "type": list_type}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data

    except HTTPError as http_err:
        if resp.status_code == 400 or resp.status_code == 409:
            # Souvent erreur 409 pour conflit / doublon
            print(
                f"Erreur : une liste avec le nom '{name_new_list}' existe déjà, merci de renseigner un nouveau nom"
            )
        else:
            print(f"Erreur HTTP {resp.status_code} : {resp.text}")
        return None


def get_id_list(name_new_list, user_token):
    try:
        data_list = create_partlist(user_token, name_new_list, list_type=1)
        id_list = data_list.get('id')
        return id_list

    except HTTPError as http_err:
        if resp.status_code == 400 or resp.status_code == 409:
            # Souvent erreur 409 pour conflit / doublon
            print(
                f"Erreur : une liste avec le nom '{name_new_list}' existe déjà."
            )
        else:
            print(f"Erreur HTTP {resp.status_code} : {resp.text}")
        return None


def delete_partlist(user_token, id_list):
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/{id_list}/"
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print("")
    else:
        print(
            f"❌ Erreur {response.status_code} lors de la suppression : {response.text}"
        )


def csv_to_json_parts(csv_file):
    """
    Lit un fichier CSV et retourne une liste de dicts JSON au format attendu par l'API Rebrickable.
    Chaque dict contient les clés : 'part_num', 'color_id', 'quantity'.
    Utilise la colonne 'Rebrickable_ID_1' pour 'part_num'.

    Paramètres :
    -----------
    csv_file : str
        Chemin vers le fichier CSV à lire.

    Retourne :
    ---------
    list[dict]
        Liste de dictionnaires JSON correspondant aux pièces.
    """
    parts_list = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            part_num = row.get("Rebrickable_ID_1")
            color_id = row.get("color_id")
            quantity = row.get("quantity")

            # Convertir color_id et quantity en int si possible, sinon valeur par défaut
            try:
                color_id = int(color_id)
            except (ValueError, TypeError):
                color_id = 9999
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                quantity = 1

            if part_num:  # On vérifie qu'il y a bien un ID Rebrickable
                parts_list.append({
                    "part_num": part_num,
                    "color_id": color_id,
                    "quantity": quantity
                })
    return parts_list


def add_parts_to_partlist(user_token, id_list, parts_list):
    """
    Ajoute ou met à jour plusieurs parts dans une Part List sur Rebrickable.

    Args:
        user_token (str): Le token utilisateur Rebrickable.
        id_list (int): L'ID de la Part List où ajouter les parts.
        parts_list (list[dict]): Liste des pièces à ajouter ou mettre à jour.

    Returns:
        bool: True si l'opération réussit, False sinon.
    """
    url_base = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/{id_list}/parts/"
    headers = {
        "Authorization": f"key {REBRICKABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Récupérer les pièces existantes dans la partlist
        response = requests.get(url_base, headers=headers)
        response.raise_for_status()
        existing_parts = {
            f"{item['part']['part_num']}-{item['color']['id']}":
            item["quantity"]
            for item in response.json().get("results", [])
        }

        for part in parts_list:
            part_key = f"{part['part_num']}-{part['color_id']}"
            quantity = part["quantity"]

            if part_key in existing_parts:
                # Met à jour la quantité avec Put
                updated_quantity = existing_parts[part_key] + quantity
                update_url = f"{url_base}{part['part_num']}/{part['color_id']}/"
                put_data = {"quantity": updated_quantity}
                put_response = requests.put(update_url,
                                            headers=headers,
                                            json=put_data)
                put_response.raise_for_status()

            else:
                # Ajoute la pièce avec POST
                post_response = requests.post(url_base,
                                              headers=headers,
                                              json=part)
                post_response.raise_for_status()

        return True

    except requests.exceptions.RequestException as err:
        print(f"❌ Erreur lors de l'ajout/mise à jour des pièces : {err}")
        return False


def get_or_create_partlist(user_token, part_list_name, list_type=1):
    """
    Vérifie si une Part List existe déjà. Si oui, retourne son ID.
    Sinon, crée une nouvelle Part List et retourne son ID.

    Args:
        user_token (str): Token utilisateur pour l'authentification.
        name_new_list (str): Nom de la liste.
        list_type (int): 1 = utilisée pour Build, 2 = non utilisée dans Build.

    Returns:
        int | None: ID de la Part List existante ou nouvellement créée, None en cas d'erreur.
    """
    url_get = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/"
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

    try:
        # Vérifie si une liste avec le même nom existe
        response = requests.get(url_get, headers=headers)
        response.raise_for_status()
        data = response.json()

        for item in data["results"]:
            if item["name"].lower() == part_list_name.lower(
            ):  # Ignore la casse
                return item["id"]

        # Si la liste n'existe pas, la créer
        url_post = url_get
        payload = {"name": part_list_name, "type": list_type}
        response = requests.post(url_post, headers=headers, json=payload)
        response.raise_for_status()
        new_list = response.json()

        return new_list["id"]

    except requests.exceptions.RequestException as err:
        print(f"Erreur lors de la requête : {err}")
        return None


def can_build_set(user_token, set_num):
    """
    Vérifie si l'utilisateur peut construire un set donné avec ses pièces.

    Args:
        user_token (str): Token utilisateur Rebrickable.
        set_num (str): Numéro du set (ex: '75301-1').
        api_key (str): Clé API Rebrickable.

    Returns:
        dict: Détails de la construction possible (pièces manquantes, % de complétion, etc.)
    """
    url = f"https://rebrickable.com/api/v3/users/{user_token}/build/{set_num}/"
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lève une erreur si la requête échoue
    return response.json()


def do_set_with_myparts(set_num, user_token):

    result = can_build_set(user_token, set_num)
    info = {
        " Set": [set_num],
        "Pieces total du set": [result.get('total_parts')],
        "% pièces possédée du set": [round(result.get('pct_owned'), 1)],
        "Nombre pièce manquante": [result.get('num_missing')],
    }

    df = pd.DataFrame(info)
    return df


def part_set(set_num):
    """
    Récupère la liste des pièces d'un set LEGO donné en interrogeant l'API Rebrickable.

    Args:
        set_num (str): Le numéro du set LEGO à rechercher.

    Returns:
        pandas.DataFrame: Un DataFrame contenant les pièces du set avec leur numéro, quantité et couleur.

    Raises:
        requests.exceptions.HTTPError: Si la requête à l'API échoue.

    Fonctionnement :
    - Envoie une requête à l'API Rebrickable pour récupérer les pièces du set spécifié.
    - Parcourt les résultats et filtre les pièces de rechange.
    - Stocke les informations essentielles (numéro de pièce, quantité, couleur).
    - Gère la pagination si plusieurs pages de résultats existent.
    - Retourne les données sous forme de DataFrame pandas.

    ATTENTION piece de rechange et minifig non incluse.
    """
    url = f"https://rebrickable.com/api/v3/lego/sets/{set_num}/parts/"
    headers = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

    rows = []
    while url:
        response = cached_session.get(url, headers=headers)
        response.raise_for_status()  # Lève une erreur si la requête échoue
        result = response.json()

        for item in result["results"]:
            # Ne pas prendre les pièces de rechange
            if item.get("is_spare", False):
                continue

            part_num = item["part"]["part_num"]
            quantity = item["quantity"]
            color = item["color"]["id"]
            rows.append({
                "part_num": part_num,
                "quantity": quantity,
                "color": color
            })

        url = result.get(
            "next")  # Passe à la page suivante si elle existe, sinon None

    df = pd.DataFrame(rows)
    return df


def part_colors(bricklink_id):
    """
    Récupère toutes les couleurs disponibles pour une pièce LEGO, à partir de son ID BrickLink.

    Args:
        bricklink_id (str): L'identifiant BrickLink.

    Returns:
        pandas.DataFrame: Un DataFrame contenant les détails des couleurs disponibles pour cette pièce.
    """

    HEADERS = {"Authorization": f"key {REBRICKABLE_API_KEY}"}
    rebrickable_id = get_rebrickable_id(bricklink_id)

    if not rebrickable_id:
        print(f" Aucun ID Rebrickable trouvé pour {bricklink_id}.")
        return pd.DataFrame()  # Retourne un DataFrame vide si aucun ID Rebrickable n'est trouvé

    url = f"https://rebrickable.com/api/v3/lego/parts/{rebrickable_id}/colors/"
    response = cached_session.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    # Construire une liste des résultats sous forme de dictionnaire
    rows = []
    for item in data["results"]:
        rows.append({
            "bricklink_id": bricklink_id,
            "rebrickable_id": rebrickable_id,
            "color_id": item["color_id"],
            "color_name": item["color_name"],
            "num_sets": item["num_sets"],
            "num_set_parts": item["num_set_parts"],
            "part_img_url": item["part_img_url"],
            # Convertit la liste en une chaîne de texte
            "elements": ', '.join(item["elements"])
        })

    # Convertir en DataFrame pandas
    df = pd.DataFrame(rows)

    return df
