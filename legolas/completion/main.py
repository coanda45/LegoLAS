import os
import pandas as pd
import datetime
import re
from urllib import request
import gzip
import shutil
import ast
from collections import defaultdict


#Functions:
def purge(dir: str, pattern: str):
    '''
    Efface tous les fichiers contenus dans le dossier dir s'il respect le pattern
    '''
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def download_csv_files() -> pd.DataFrame:
    '''
    Récupère les csv du jour s'il ne sont pas déjà présents dans le dossier
    tmp. Si les fichiers présents sont ceux de jours passés, on les efface
    et on les remplace par les gz du jour.
    On les unzip et au final on créé les dataframe.
    '''
    #récupération des csv
    #url
    inventories_path = 'https://cdn.rebrickable.com/media/downloads/inventories.csv.gz'
    inventories_parts_path = 'https://cdn.rebrickable.com/media/downloads/inventory_parts.csv.gz'
    sets_path = 'https://cdn.rebrickable.com/media/downloads/sets.csv.gz'

    #date du jour
    today = datetime.date.today()
    today_f = datetime.datetime.strftime(today, '%y%m%d')

    #on récupère les noms des fichiers
    inventories_name = re.split(pattern='/', string=inventories_path)[-1]
    inventories_parts_name = re.split(pattern='/',
                                      string=inventories_parts_path)[-1]
    sets_path_name = re.split(pattern='/', string=sets_path)[-1]

    #ajout today date aux noms des ficheirs gz
    inventories_dated_name = inventories_name[:-3] + "_" + today_f + '.gz'
    inventories_parts_dated_name = inventories_parts_name[:
                                                          -3] + "_" + today_f + '.gz'
    sets_dated_name = sets_path_name[:-3] + "_" + today_f + '.gz'

    #liens de sauvegarde des gz renommés
    tmp_dir = '/tmp'  #os.path.dirname(__file__) +
    file_inventories_path = f'{tmp_dir}/{inventories_dated_name}'
    file_inventories_parts_path = f'{tmp_dir}/{inventories_parts_dated_name}'
    file_sets_path = f'{tmp_dir}/{sets_dated_name}'

    #si les fichier gz datés du jour existent déjà, on ne les retélécharge pas.
    #sinon, on efface l'ancien gz et les csv unzippés.
    if not os.path.isfile(file_inventories_path):
        #s'il n'existe pas, on efface l'ancien fichier csv et gz
        #s'il existe, on ne fait rien (on ne redl pas et on ne dezip pas)
        dir = os.listdir(tmp_dir)
        # Checking if the list is empty or not
        if len(dir) > 0:
            purge(tmp_dir, '/inventories.csv')

        r_inv = request.urlretrieve(url=inventories_path,
                                    filename=file_inventories_path)

    if not os.path.isfile(file_inventories_parts_path):
        #s'il n'existe pas on efface l'ancien fichier csv et gz
        #s'il existe, on ne fait rien (on ne redl pas et on ne dezip pas)
        dir = os.listdir(tmp_dir)
        # Checking if the list is empty or not
        if len(dir) > 0:
            purge(tmp_dir, '/inventory_parts.csv')
        r_inv_parts = request.urlretrieve(url=inventories_parts_path,
                                          filename=file_inventories_parts_path)

    if not os.path.isfile(file_sets_path):
        #s'il n'existe pas on efface l'ancien fichier csv et gz
        #s'il existe, on ne fait rien (on ne redl pas et on ne dezip pas)
        dir = os.listdir(tmp_dir)
        # Checking if the list is empty or not
        if len(dir) > 0:
            purge(tmp_dir, '/sets.csv')
        r_sets = request.urlretrieve(url=sets_path, filename=file_sets_path)


    #creations dataframes
    df_inventories = pd.read_csv(file_inventories_path,
                                 compression='gzip',
                                 header=0,
                                 sep=',',
                                 on_bad_lines='skip')

    df_inventory_parts = pd.read_csv(file_inventories_parts_path,
                                     compression='gzip',
                                     header=0,
                                     sep=',',
                                     on_bad_lines='skip')

    df_sets = pd.read_csv(file_sets_path,
                          compression='gzip',
                          header=0,
                          sep=',',
                          on_bad_lines='skip')

    return df_inventories, df_inventory_parts, df_sets


# A effacer après intégration dans le workflow
def generate_test_liste_part_disponible() -> list:
    '''
    A remplacer par la liste récupérée après l'API de Cassille
    '''
    liste_parts_disponibles = [
        {
            'part_num': '2343',
            'quantity': 1,
            'color_id': 45
        },
        {
            'part_num': '3003',
            'quantity': 1,
            'color_id': 29
        },
        {
            'part_num': '30176',
            'quantity': 1,
            'color_id': 2
        },
        {
            'part_num': '3020',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '3022',
            'quantity': 2,
            'color_id': 15
        },
        {
            'part_num': '3023',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '30357',
            'quantity': 4,
            'color_id': 29
        },
        {
            'part_num': '3039',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '3062b',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '3068b',
            'quantity': 1,
            'color_id': 29
        },
        {
            'part_num': '3069b',
            'quantity': 5,
            'color_id': 27
        },
        {
            'part_num': '3069b',
            'quantity': 2,
            'color_id': 29
        },
        {
            'part_num': '33291',
            'quantity': 3,
            'color_id': 191
        },
        {
            'part_num': '3795',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '3941',
            'quantity': 1,
            'color_id': 27
        },
        {
            'part_num': '3960',
            'quantity': 1,
            'color_id': 27
        },
        {
            'part_num': '4032a',
            'quantity': 1,
            'color_id': 70
        },
        {
            'part_num': '4865a',
            'quantity': 3,
            'color_id': 41
        },
        {
            'part_num': '6141',
            'quantity': 2,
            'color_id': 27
        },  #4
        {
            'part_num': '6141',
            'quantity': 1,
            'color_id': 29
        },  #4
        {
            'part_num': '63965',
            'quantity': 1,
            'color_id': 15
        },
        {
            'part_num': '85080',
            'quantity': 4,
            'color_id': 322
        },  #4
        #pièce en trop:
        {
            'part_num': '48395',
            'quantity': 1,
            'color_id': 7
        },
        {
            'part_num': '48864c01',
            'quantity': 1,
            'color_id': 25
        }
    ]
    return liste_parts_disponibles


def list_set_contenant_au_moins_une_des_pieces(list_part_num: dict,
                                               nombre_part_min_par_set: int = 5
                                               ) -> pd.DataFrame:
    '''
    Sur la base d'un dictionnaire de part_num disponibles (list_part_num), la
    fonction renvoie une dataframe avec l'ensemble des sets utilisant au moins
    une pièce présente dans le dictionnaires des pièces fournies.
    Un "vrai" correspondant à un set ayant au moins 5 part_num différents, ce
    qui permet d'éviter d'afficher des sets contenant un seul type de pièce mais
    dans des couleurs différentes. En gros un set "intéressant à construire".

    INPUT:
        list_part_num: dictionnaire au format :
        list_part_num = [
                            {
                                'part_num': '2343',
                                'quantity': 1,
                                'color_id': 45
                            },
                            {...},...
        ]
        nombre_part_min_par_set : entier, par défaut égal à 5

    OUTPUT :
        une dataframe avec une ligne par set
        colonnes =
            inventory_id : l'id correspondant à la clé primaire
            part_num_agg : aggrégation des part_nums sans tenir compte des
                couleurs
            count_nb_part_different	: le nombre de part_nums différents
            quantity_total_part_num	 : le nombre total de pièces (sans spare),
                hors figurines
            part_num_qty_color : une liste contenant les dictionnaires avec
                les part_num, les quantité et les color_id des pièces de
                chaque set
            set_num : le numéro LEGO du set correspondant à l'inventory_id
    '''

    liste_pieces = [elem['part_num'] for elem in list_part_num]

    #on récupère uniquement les lignes des pièces du set et pas le spare
    df_set_sans_spare = df_inventory_parts[df_inventory_parts['is_spare'] ==
                                           False].copy().reset_index(drop=True)
    #on créé un pattern avec toutes les pièces pour filtrer le dataframe
    pattern = '|'.join(liste_pieces)
    mask = df_set_sans_spare['part_num'].str.contains(pattern).fillna(False)

    #on récupère la dataframe
    df = df_set_sans_spare[mask].copy().reset_index(drop=True)

    #on récupère la liste des inventory_id uniques
    liste_inventory_id_cites_unique = df['inventory_id'].unique()

    #on récupère l'ensemble des lignes du dataframe initial pour lequel
    #le inventory id est dans la liste des set possible.
    df_filtree_set_pertinents = df_set_sans_spare[df_set_sans_spare[
        'inventory_id'].isin(liste_inventory_id_cites_unique)].copy()

    #fonction pour aggreger les part num
    f = lambda x: ','.join(sorted(list(set(x))))

    #on créé une dataframe avec la concaténation des part_num
    df_2 = df_filtree_set_pertinents.groupby(
        'inventory_id', as_index=False).agg(part_num_agg=('part_num', f))
    #on créé une colonne avec la concaténation des part_num, qty et color dans une liste
    # df['part_num_qty_color']=df[['part_num', 'quantity', 'color_id']].values.tolist()
    # print(df_2)

    df_filtree_set_pertinents['part_num_qty_color']=[\
        {'part_num': elem[0], 'quantity': elem[1], 'color_id': elem[2]} \
        for elem in \
            df_filtree_set_pertinents[['part_num', 'quantity', 'color_id']].values.tolist()]

    # print(df)
    #on créé une dataframe avec un groupby des listes des différentes partnum (pour conserver la qté et la color)
    df_concat_list = df_filtree_set_pertinents.groupby(
        'inventory_id', as_index=False)['part_num_qty_color'].apply(list)
    # print(df_concat_list)

    #on group by inventory et part_num. Il peut y avoir plusieurs lignes
    #pour un même part_num mais sous différentes couleurs. Ca fausse le count
    #si on fait tout d'un coup
    df_3 = df_filtree_set_pertinents.groupby(
        ['inventory_id', 'part_num'],
        as_index=False).agg(count_nb_part_different=('part_num', 'count'),
                            quantity_total_part_num=('quantity', "sum"))
    # print(df_3)
    #on groupby la précédent df sur les inventaire pour avoir le bon
    #count de num_part
    df_4 = df_3.groupby('inventory_id', as_index=False).agg(
        count_nb_part_different=('count_nb_part_different', 'count'),
        #part_num_agg=('part_num', f),
        quantity_total_part_num=('quantity_total_part_num', "sum"))
    # print(df_4)
    #on prend que des sets avec suffisamment de part différentes
    df_final = pd.merge(df_2, df_4, how='inner', on='inventory_id')
    df_final = pd.merge(df_final,
                        df_concat_list,
                        how='inner',
                        on='inventory_id')
    df_final = df_final[df_final['count_nb_part_different'] >=
                        nombre_part_min_par_set]
    df_final = pd.merge(df_final,
                        df_inventories,
                        how='left',
                        left_on='inventory_id',
                        right_on='id').drop(columns=['id', 'version'])
    return df_final


def available_part_num_dict(liste_part_dispo: dict) -> dict:
    '''
    Function créant des dictionnaires avec les pièces disponibles, que l'on tienne compte ou non des couleurs

    INPUT :
        liste des part_num disponibles : liste de dictionnaire au format:
            liste_parts_disponibles = [
        {
            'part_num': '2343',
            'quantity': 1,
            'color_id': 45
        },
        ...
        {}
        ]

    OUTPUT :
        available_qty : dictionnaire au format:
            {
            (partnum, color_id) : quantity,
            (partnum, color_id) : quantity,
            ....
            }
        available_qty_no_color : dictionnaire au format:
            {
            partnum : quantity,
            partnum : quantity,
            ....
            }
    '''
    available_qty = defaultdict(int)
    for item in liste_part_dispo:
        key = (item['part_num'], item['color_id'])
        available_qty[key] += item['quantity']

    available_qty_no_color = defaultdict(int)
    for item in liste_part_dispo:
        key = item['part_num']
        available_qty_no_color[key] += item['quantity']

    return available_qty, available_qty_no_color


def compute_colour_match(row, available_qty: dict,
                         available_qty_no_color: dict) -> pd.Series:
    '''
    Fonction générant une nouvelle Pandas Series pour chaque row passée à
    la fonction.

    INPUT :
        La ligne à utiliser, et les dictionnaires des pièces disponibles si on
        tient compte ou non des couleurs.

    OUTPUT :
        une Pandas Series avec 7 colonnes:
            'percent_no_colour'
            'missing_without_color'
            'extra_part_without_color'
            'percent_colour_match'
            'exact_available_parts'
            'missing_exact_parts'
            'extra part with color'
    '''
    # Parse JSON‑like string safely
    # 'part_num_qty_color'  liste de dictionnaires avec toutes les infos sur
    # les pièces nécessaire pour faire un set.
    #[{'part_num': '48379c04', 'quantity': 1, 'color_id' : 15},{...}...
    required_list = ast.literal_eval(str(row['part_num_qty_color']))
    required_part_num_no_color = []

    # Aggregate requirements by (part_num, color_id)
    req_qty_color = defaultdict(int)
    for rec in required_list:
        key = (rec['part_num'], rec['color_id'])
        required_part_num_no_color.append(key[0])
        req_qty_color[key] += rec['quantity']
    #nombre de pièces totales nécessaire pour faire le set
    total_req = sum(req_qty_color.values())

    #initialisation des variables et listes nécessaire
    matched_total_color = 0
    matched_total_without_color = 0
    missing_without_color = []
    exact_available = []
    missing_exact = []
    extra_part_no_color = []
    extra_part_with_color = []

    #on tient compte des couleurs
    available_qty_copy = available_qty.copy()
    for key, req_q in req_qty_color.items():
        #on regarde si la pièce et la couleur sont bonnes
        #on récupère la quantité disponible ou zéro
        avail_q = available_qty.get(key, 0)
        #Si on a moins ou pas d epièce nécessaire, on récupère cette valeur
        #sinon on récupère la valeur requise.
        matched_q = min(avail_q, req_q)
        #On ajoute la valeur aux pièces totales
        matched_total_color += matched_q

        if matched_q:
            exact_available.append({
                'part_num': key[0],
                'color_id': key[1],
                'qty_match': matched_q,
            })
        if matched_q < req_q:
            missing_exact.append({
                'part_num': key[0],
                'color_id': key[1],
                'qty_missing': req_q - matched_q,
            })

        #on a utilisé cette key. On la supprime pour ne conserver que les extra part num
        if key in available_qty_copy:
            available_qty_copy.pop(key)

    #s'il reste des pièces dans available_qty_copy, alors ce sont des pièces en trop.
    if available_qty_copy is not None:
        for key, req_q in available_qty_copy.items():
            # si le partnum n'est pas dans les pièces nécessaire, alors cette pièce
            # est inutile dans le set que l'on tienne compte ou non des couleurs
            # on l'ajoute donc dans les 2 extra_part list
            if key[0] not in required_part_num_no_color:
                extra_part_with_color.append({
                    'part_num': key[0],
                    'color_id': key[1],
                    'extra_qty': req_q,
                })
                extra_part_no_color.append({
                    'part_num': key[0],
                    'color_id': key[1],
                    'extra_qty': req_q,
                })
            # sinon, la pièce est nécessaire au set mais elle n'est pas de la bonne couleur
            # c'est donc une extra_part si on tient compte des couleurs.
            else:
                extra_part_with_color.append({
                    'part_num': key[0],
                    'color_id': key[1],
                    'extra_qty': req_q,
                })

    #on regarde sans tenir compte des couleurs:
    # Aggregate requirements by part_num
    req_qty_no_color = defaultdict(int)
    for rec in required_list:
        key = rec['part_num']
        req_qty_no_color[key] += rec['quantity']

    for key_no_color, req_q_no_color in req_qty_no_color.items():
        avail_q_no_color = available_qty_no_color.get(key_no_color, 0)
        #Si on a moins ou pas de pièce nécessaire, on récupère cette valeur
        #sinon on récupère la valeur requise.
        matched_q_no_color = min(avail_q_no_color, req_q_no_color)
        #On ajoute la valeur aux pièces totales
        matched_total_without_color += matched_q_no_color

        if not matched_q_no_color:
            missing_without_color.append({
                'part_num': key_no_color,
                'qty_missing': req_q_no_color,
            })
        if matched_q_no_color < req_q_no_color:
            missing_without_color.append({
                'part_num':
                key_no_color,
                'qty_missing':
                req_q_no_color - matched_q_no_color,
            })
    #ici pas besoin de regarder les extra part, on l'a déjà fait avant.

    percent_exact_without_color = round(
        matched_total_without_color / total_req * 100, 2) if total_req else 0

    percent_exact_color = round(matched_total_color / total_req *
                                100, 2) if total_req else 0

    return pd.Series({
        'percent_no_colour': percent_exact_without_color,
        'missing_without_color': missing_without_color,
        'extra_part_without_color': extra_part_no_color,
        'percent_colour_match': percent_exact_color,
        'exact_available_parts': exact_available,
        'missing_exact_parts': missing_exact,
        'extra part with color': extra_part_with_color,
    })


def generate_final_df(sets_df: pd.DataFrame, available_qty: dict,
                      available_qty_no_color: dict, df_sets) -> pd.DataFrame:
    '''
    Fonction générant les résultats finaux:
    On récupère les 10 sets les plus faisables, que l'on tienne compte ou
    non des couleurs, triés par pourcentage de pièces disponibles.
    On récupère aussi le lien vers la photo des sets.

    INPUT :
        - sets_df = la dataframe générée contenant l'ensemble des sets utilisant au moins
        une pièce parmi la liste des pièes disponibles.
        - les dictionnaires des pièces disponibles si on
        tient compte ou non des couleurs.
        - df_sets : dataframe reliant les numéro de set aux photos hébergées sur
        le site de rebrickable

    OUTPUT :
        - les 10 sets les plus faisables si on tient compte des couleurs
        - les 10 set les plus faisables si on ne tient pas compte des couleurs

    '''
    #génération de la dataframe globale
    colour_metrics = sets_df.apply(lambda x: compute_colour_match(
        x, available_qty, available_qty_no_color),
                                   axis=1)
    df_total = pd.concat([sets_df, colour_metrics], axis=1)

    #génération des dataframes des 10 sets les plus faisables si on tient compte des couleurs ou non
    df_no_color = df_total[[
        'inventory_id', 'set_num', 'percent_no_colour',
        'missing_without_color', 'extra_part_without_color'
    ]].copy().sort_values(ascending=False, by='percent_no_colour').head(10)
    df_color = df_total[[
        'inventory_id', 'set_num', 'percent_colour_match',
        'missing_exact_parts', 'extra part with color'
    ]].copy().sort_values(ascending=False, by='percent_colour_match').head(10)

    #Transformation des dataframes obtenus pour ne conserver que des lists au
    #lieu des dict
    df_no_color_final = df_no_color.copy()
    df_no_color_final['missing_without_color'] = df_no_color_final[
        'missing_without_color'].apply(
            lambda x: [[elem['part_num'], elem['qty_missing']]
                       if len(elem) > 0 else [] for elem in x])
    df_no_color_final['extra_part_without_color'] = df_no_color_final[
        'extra_part_without_color'].apply(
            lambda x: [[elem['part_num'], elem['extra_qty']]
                       if len(elem) > 0 else [] for elem in x])
    df_no_color_final.reset_index(drop=True, inplace=True)

    df_color_final = df_color.copy()
    df_color_final['missing_exact_parts'] = df_color[
        'missing_exact_parts'].apply(lambda x: [[
            elem['part_num'], elem['color_id'], elem['qty_missing']
        ] if len(elem) > 0 else [] for elem in x])
    df_color_final['extra part with color'] = df_color_final[
        'extra part with color'].apply(
            lambda x: [[elem['part_num'], elem['color_id'], elem['extra_qty']]
                       if len(elem) > 0 else [] for elem in x])
    df_color_final.reset_index(drop=True, inplace=True)

    # ajout des liens vers l'image des sets
    df_no_color_final_lien = pd.merge(
        df_no_color_final, df_sets, how='left',
        on='set_num').drop(columns=['name', 'year', 'theme_id', 'num_parts'])
    df_color_final_lien = pd.merge(
        df_color_final, df_sets, how='left',
        on='set_num').drop(columns=['name', 'year', 'theme_id', 'num_parts'])

    return df_no_color_final_lien, df_color_final_lien


if __name__ == "__main__":
    #Récupération des csv et génération des dataframes
    df_inventories, df_inventory_parts, df_sets = download_csv_files()
    #A modifier avec le buffer.
    liste_part_dispo = generate_test_liste_part_disponible()
    #génération de la dataframe avec tous les sets utilisant au moins 1 part_num
    # de la liste des pièces dispo
    sets_df = list_set_contenant_au_moins_une_des_pieces(liste_part_dispo)
    #creation des dict des pièces disponibles
    available_qty, available_qty_no_color = available_part_num_dict(
        liste_part_dispo)
    #génération de la dataframe avec les pourcentages
    df_no_color_final, df_color_final = generate_final_df(
        sets_df, available_qty, available_qty_no_color, df_sets)

    print(df_no_color_final)
    print(df_color_final)
