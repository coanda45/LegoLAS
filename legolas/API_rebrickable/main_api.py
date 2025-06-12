

import requests
import csv
import time
import os
import csv
import json
from requests.exceptions import HTTPError
import pandas as pd

KEY_USER = "91e7670a51c5f4decf0dc3cd270c973d"

def export_bricklink_to_rebrickable_csv(bricklink_ids, output_file="list_parts.csv"):
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
    HEADERS = {"Authorization": f"key {KEY_USER}"}
    URL = "https://rebrickable.com/api/v3/lego/parts/"

    all_results = []
    existing_data = {}
    max_ids_per_row = 0

    #Lire les données existantes (s'il y a un fichier)
    if os.path.isfile(output_file):
        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                bl_id = row[0]
                color_id = row[1]
                quantity = int(row[2])
                rebrickable_ids = row[3:]
                existing_data[bl_id] = [bl_id, int(color_id), quantity] + rebrickable_ids
                max_ids_per_row = max(max_ids_per_row, len(rebrickable_ids))

    for idx, bl_id in enumerate(bricklink_ids):
        print(f"[{idx+1}/{len(bricklink_ids)}] Recherche : {bl_id}")
        try:
            params = {"bricklink_id": bl_id}
            response = requests.get(URL, headers=HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            rebrickable_ids = [part["part_num"] for part in results] if results else []
        except Exception as e:
            print(f"❌ Erreur pour {bl_id} : {e}")
            rebrickable_ids = []

        max_ids_per_row = max(max_ids_per_row, len(rebrickable_ids))

        if bl_id in existing_data:
            existing_data[bl_id][2] += 1  # Incrémenter la quantité
        else:
            existing_data[bl_id] = [bl_id, 9999, 1] + rebrickable_ids

    # Réécriture complète avec header dans l’ordre souhaité
    header = ["Bricklink_ID", "color_id", "quantity"] + [f"Rebrickable_ID_{i+1}" for i in range(max_ids_per_row)]

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in existing_data.values():
            # Compléter avec des colonnes vides si nécessaire
            row += [""] * (len(header) - len(row))
            writer.writerow(row)

    print(f"\n✅ Fichier CSV mis à jour : {output_file}")

def get_user_token(USER_NAME, PASSWORD):
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
    - La variable globale `KEY_USER` doit être définie avant l'appel de cette fonction.
    - Ce token peut être utilisé ensuite pour authentifier des requêtes spécifiques à l'utilisateur (sets, lists, etc.).
    """
    URL = "https://rebrickable.com/api/v3/users/_token/"

    data = {
        'username': USER_NAME,
        'password': PASSWORD
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'key {KEY_USER}'
    }

    response = requests.post(URL, data=data, headers=headers)

    if response.status_code == 200:
        user_token = response.json().get('user_token')
        return user_token
    else:
        print(f"Erreur {response.status_code} : {response.text}")
        return None

def create_partlist(user_token, name_new_list,list_type=1):
    """
    Crée une nouvelle Part List.
    - name (str): nom de la liste.
    - list_type (int): 1 = utilisée pour Build, 2 = non utilisée dans Build.

    Retourne : JSON avec le détail de la liste créée.
    """
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/"
    headers = {"Authorization": f"key {KEY_USER}"}
    payload = {"name": name_new_list , "type": list_type}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data= resp.json()
        return data

    except HTTPError as http_err:
        if resp.status_code == 400 or resp.status_code == 409:
            # Souvent erreur 409 pour conflit / doublon
            print(f"Erreur : une liste avec le nom '{name_new_list}' existe déjà, merci de renseigner un nouveau nom")
        else:
            print(f"Erreur HTTP {resp.status_code} : {resp.text}")
        return None

def get_id_list(name_new_list,user_token):
    try:
        data_list = create_partlist(user_token, name_new_list ,list_type=1)
        id_list = data_list.get('id')
        return id_list

    except HTTPError as http_err:
        if resp.status_code == 400 or resp.status_code == 409:
            # Souvent erreur 409 pour conflit / doublon
            print(f"Erreur : une liste avec le nom '{name_new_list}' existe déjà.")
        else:
            print(f"Erreur HTTP {resp.status_code} : {resp.text}")
        return None

def delete_partlist(user_token, id_list):
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/{id_list}/"
    headers = {"Authorization": f"key {KEY_USER}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"✅ Partlist {id_list} supprimée avec succès.")
    else:
        print(f"❌ Erreur {response.status_code} lors de la suppression : {response.text}")

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

def add_parts_to_partlist(user_token, id_list, json_parts):
    """
    Ajoute plusieurs parts à une partlist Rebrickable.

    Args:
        user_token (str): Le token utilisateur Rebrickable.
        list_id (int): L'ID de la partlist où ajouter les parts.
        parts (list of dict): Liste de parts au format [{"part_num": str, "color_id": int, "quantity": int}, ...]
        api_key (str): Clé API Rebrickable.

    Returns:
        list: Liste des parts ajoutées avec succès (réponse JSON).
    """
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/{id_list}/parts/"
    headers = {
        "Authorization": f"key {KEY_USER}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=json_parts)
    response.raise_for_status()
    print(f"Les pièces ont bien été ajoutées à la liste")

def can_build_set(user_token,set_num):
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
    headers = {
        "Authorization": f"key {KEY_USER}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lève une erreur si la requête échoue
    return response.json()

def do_set_with_myparts(set_num, user_token):

    result=can_build_set(user_token, set_num)
    info = {" Set":[set_num],
            "Pieces total du set": [result.get('total_parts')],
        "% pièces possédée du set" : [round(result.get('pct_owned'),1)],
        "Nombre pièce manquante" : [result.get('num_missing')],
        }

    df=pd.DataFrame(info)
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
    headers = {
        "Authorization": f"key {KEY_USER}"
    }

    rows = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une erreur si la requête échoue
        result = response.json()

        for item in result["results"]:
            # Ne pas prendre les pièces de rechange
            if item.get("is_spare", False):
                continue

            part_num = item["part"]["part_num"]
            quantity = item["quantity"]
            color = item["color"]["id"]
            rows.append({"part_num": part_num, "quantity": quantity, "color": color})

        url = result.get("next")  # Passe à la page suivante si elle existe, sinon None

    df = pd.DataFrame(rows)
    return df
