import requests
import pandas as pd


def classify_part(img_data):
    """
    Analyse une image LEGO via l'API Brickognize et retourne un DataFrame contenant les résultats.

    Args:
        image_path (str): Chemin d'accès à l'image à analyser.

    Returns:
        pd.DataFrame: Tableau contenant les informations des pièces LEGO détectées, incluant :
            - id (str) : Identifiant de la pièce LEGO
            - name (str) : Nom de la pièce LEGO
            - img_url (str) : URL de l'image de la pièce LEGO
            - category (str) : Catégorie de la pièce LEGO
            - external_site_name (str) : Nom du site externe lié à la pièce
            - external_site_url (str) : URL du site externe

    Raises:
        ValueError: Si la requête à l'API échoue ou si aucune pièce LEGO n'est détectée.

    Example:
        >>> df = classification("/path/to/image.jpeg")
        >>> print(df.head())
    """

    # with open(image_path, "rb") as img_file:
    #     img_data = img_file.read()

    url = "https://api.brickognize.com/predict/"

    files = {
        'query_image': ('image.jpg', img_data, 'image/jpeg')
    }

    headers = {
        'accept': 'application/json'
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        response_json = response.json()
        response_items = response_json['items']
        df = pd.DataFrame(response_items)
        # print(df)
        return df

    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return pd.DataFrame()
