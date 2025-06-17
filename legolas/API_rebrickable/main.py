import requests
from requests.exceptions import HTTPError
import pandas as pd
from main_api import get_user_token, add_parts_to_partlist, get_or_create_partlist, delete_partlist


def add_parts_to_username_partlist(user_name, password, part_list_name,
                                   parts_list):
    user_token = get_user_token(user_name, password)

    if user_token:
        id_list = get_or_create_partlist(user_token,
                                         part_list_name,
                                         list_type=1)

        if id_list:
            add_parts_to_partlist(user_token, id_list, parts_list)
            return f"https://rebrickable.com/users/{user_name}/partlists/{id_list}/"

    return "Error Rebrickable"


if __name__ == "__main__":
    parts_list = [{
        'part_num': '3004',
        'color_id': 9999,
        'quantity': 10
    }, {
        'part_num': '3006',
        'color_id': 9999,
        'quantity': 3
    }, {
        'part_num': '2745stor',
        'color_id': 9999,
        'quantity': 4
    }]
    user_name = 'Legolas2007'
    password = 'Lewagon2007'
    part_list_name = 'nom_de_la_list5'

    result = add_parts_to_username_partlist(user_name, password,
                                            part_list_name, parts_list)

    print(result)

    # ✅ Ajout de la question pour supprimer la liste
    user_token = get_user_token(user_name, password)
    id_list = get_or_create_partlist(user_token, part_list_name, list_type=1)

    user_choice = input(
        f"🔴 Voulez-vous supprimer la liste '{part_list_name}' ? (Y/N) : "
    ).strip().lower()
    if user_choice in ["y", "yes", "o", "oui"]:
        delete_partlist(user_token, id_list)
    else:
        print("La liste est conservée.")
