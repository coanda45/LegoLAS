import requests
import csv
import time
import os
import csv
import json
from requests.exceptions import HTTPError
import pandas as pd

KEY_USER = "91e7670a51c5f4decf0dc3cd270c973d"
USER_NAME = 'Legolas2007'
PASSWORD = 'Lewagon2007'
part_list_name = 'nom_de_la_list'

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

def get_partlists(user_token):
    """
    Récupère la liste des Part Lists de l'utilisateur sur Rebrickable.

    Args:
        user_token (str): Token utilisateur pour l'authentification.

    Returns:
        dict | None: JSON contenant les Part Lists ou None en cas d'erreur.
    """
    url = f"https://rebrickable.com/api/v3/users/{user_token}/partlists/"
    headers = {"Authorization": f"key {KEY_USER}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifie si la requête est valide
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f" Erreur HTTP : {http_err}")
        return None

def add_parts_to_username_partlist():
