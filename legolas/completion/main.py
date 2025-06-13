import os
import pandas as pd

#Functions:


def list_set_contenant_au_moins_une_des_pieces(list_part_num: dict,
                                               nombre_part_min_par_set: int = 5
                                               ):
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
                                           False]
    #on créé un pattern avec toutes les pièces pour filtrer le dataframe
    pattern = '|'.join(liste_pieces)
    mask = df_set_sans_spare['part_num'].str.contains(pattern).fillna(False)

    #on récupère la dataframe
    df = df_set_sans_spare[mask].copy()

    #fonction pour aggreger les part num
    f = lambda x: ','.join(sorted(list(set(x))))

    #on créé une dataframe avec la concaténation des part_num
    df_2 = df.groupby('inventory_id',
                      as_index=False).agg(part_num_agg=('part_num', f))
    #on créé une colonne avec la concaténation des part_num, qty et color dans
    # une liste
    df['part_num_qty_color']=[\
        {'part_num': elem[0], 'quantity': elem[1], 'color_id': elem[2]} \
        for elem in \
            df[['part_num', 'quantity', 'color_id']].values.tolist()]

    #on créé une dataframe avec un groupby des listes des différentes partnum
    # (pour conserver la qté et la color)
    df_concat_list = df.groupby(
        'inventory_id', as_index=False)['part_num_qty_color'].apply(list)

    #on group by inventory et part_num. Il peut y avoir plusieurs lignes
    #pour un même part_num mais sous différentes couleurs. Ca fausse le count
    #si on fait tout d'un coup
    df_3 = df.groupby(['inventory_id', 'part_num'],
                      as_index=False).agg(count_nb_part_different=('part_num',
                                                                   'count'),
                                          quantity_total_part_num=('quantity',
                                                                   "sum"))

    #on groupby la précédent df sur les inventaire pour avoir le bon
    #count de num_part
    df_4 = df_3.groupby('inventory_id', as_index=False).agg(
        count_nb_part_different=('count_nb_part_different', 'count'),
        #part_num_agg=('part_num', f),
        quantity_total_part_num=('quantity_total_part_num', "sum"))

    #on prend que des sets avec suffisamment de part différentes
    df_final = pd.merge(df_2, df_4, how='inner', on='inventory_id')

    df_final = pd.merge(df_final,
                        df_concat_list,
                        how='inner',
                        on='inventory_id')

    df_final = df_final[df_final['count_nb_part_different'] >=
                        nombre_part_min_par_set]

    #on merge avec inventories pour récupérer la colonne 'set_num'
    df_final = pd.merge(df_final,
                        df_inventories,
                        how='left',
                        left_on='inventory_id',
                        right_on='id').drop(columns=['id', 'version'])

    return df_final


def pourcentage_piece_manquante(list_part_dispo, set_num_inventory_id,
                                df_filtree):
    '''
    Fonction retournant les:
        - le pourcentage de pièces disponibles si on ne tient pas compte
        de la couleur
        - la liste des pièces manquantes sans tenir compte de la couleur
        - le pourcentage de pièces disponibles si on tient compte de la couleur
        - la liste des pièces manquantes en tenant compte de la couleur
        - la liste des pièces disponibles mais avec la mauvaise couleur
        - les pièces extra inutiles pour chaque set.

    INPUT :
        list_part_dispo: dictionnaire au format :
            list_part_dispo = [
                                {
                                    'part_num': '2343',
                                    'quantity': 1,
                                    'color_id': 45
                                },
                                {...},...
            ]
        set_num_inventory_id : le numéro du set testé
        df_filtree : dataframe listant les sets utilisant au moins une des pièces
        disponibles, résultat de la fonction :
        list_set_contenant_au_moins_une_des_pieces

    OUTPUT :
        - le pourcentage de pièces disponibles si on ne tient pas compte
        de la couleur
        - la liste des pièces manquantes sans tenir compte de la couleur
        - le pourcentage de pièces disponibles si on tient compte de la couleur
        - la liste des pièces manquantes en tenant compte de la couleur
        - la liste des pièces disponibles mais avec la mauvaise couleur,
            dans le même format que
        - les pièces extra inutiles pour chaque set.
    '''
    #initialisation
    liste_piece_manquantes_without_color = []
    liste_piece_manquantes_with_color = []
    list_available_part_num_bad_color = []
    extra_part_num = []
    count_with_color = 0
    count_without_color = 0

    #Préparation set
    #on filtre sur le numéro de set souhaité
    df_set_num = df_filtree[df_filtree['inventory_id'] ==
                            set_num_inventory_id].reset_index(drop=True)
    #on récupère la liste totale des part_num, qté, color pour le set.
    liste_infos_set = df_set_num.loc[0, 'part_num_qty_color'].copy()
    #on trie par part_num puis color_id
    liste_infos_set = sorted(liste_infos_set,
                             key=lambda x: (x['part_num'], x['color_id']))
    # on créé une liste avec toutes les parts_num nécessaire pour un set
    # On n'a qu'une seule liste (1 seul set)
    # ici on récupère la liste des partnum. Il peut y avoir des doublons si on a
    # la même pièce mais dans différentes couleurs. C'est nécessaire pour la
    # loop suivante
    list_part_set = [elem['part_num'] for elem in liste_infos_set]

    # Préparation pièce dispo
    list_infos_part_dispo_fct = list_part_dispo.copy()
    #on trie par part_num puis color_id
    list_infos_part_dispo_fct = sorted(list_infos_part_dispo_fct,
                                       key=lambda x:
                                       (x['part_num'], x['color_id']))
    liste_part_num_dispo = [
        elem['part_num'] for elem in list_infos_part_dispo_fct
    ]

    #on boucle sur la liste des pièces nécessaires pour le set:
    for num_part_set in list_part_set:
        #si cette pièce est dans les pièces dispo
        if num_part_set in liste_part_num_dispo:
            # on boucle sur la liste de part_num_qty_color du set
            for liste_num_part_set in liste_infos_set:
                #si les num_part matchent, on récupère la quantité nécessaire
                #et la couleur nécessaire pour le set, puis on sort de la boucle
                if num_part_set == liste_num_part_set['part_num']:
                    #on récupère l'index dans la liste pour la retirer ensuite
                    #cela permet en cas de pièce avec plusieurs couleurs
                    #de supprimer la liste déjà traitée pour passer à la
                    #liste de la même pièce mais avec une autre couleur
                    index = liste_infos_set.index(liste_num_part_set)

                    qty_num_part_set = liste_num_part_set['quantity']
                    color_id_set = liste_num_part_set['color_id']
                    #on retire l'élément traité
                    liste_infos_set.pop(index)
                    break

            # on filtre dans les pièces dispo pour rechercher la bonne part_num
            # et récupérer la quantité et la couleur de la pièce dispo
            for elem in list_infos_part_dispo_fct:
                if elem['part_num'] == num_part_set:
                    qty_num_part_dispo = elem['quantity']
                    color_num_part_dispo = elem['color_id']

                    #on récupère l'index de la partie des pièces dispo
                    index = list_infos_part_dispo_fct.index({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_dispo,
                        'color_id':
                        color_num_part_dispo
                    })

                    # qty_num_part_set = liste_num_part_set['quantity']
                    # color_id_set = liste_num_part_set['color_id']

                    #on retire l'élément traité
                    list_infos_part_dispo_fct.pop(index)

                    break

            #on compare la valeur nécessaire dans le set à celle disponible
            #dans le stock. Si la valeur disponible dans le stock est supérieure
            #ou égale à celle nécessaire au set, on prend en compte le nb
            #nécessaire au set pour éviter les pourcentage finaux > 100 %
            if qty_num_part_dispo >= qty_num_part_set:
                count_without_color += qty_num_part_set
                if color_num_part_dispo == color_id_set:
                    count_with_color += qty_num_part_set
                    if qty_num_part_dispo > qty_num_part_set:
                        extra_part_num.append({
                            'part_num': num_part_set,
                            'quantity': qty_num_part_dispo - qty_num_part_set,
                            'color_id': color_num_part_dispo
                        })
                else:
                    list_available_part_num_bad_color.append({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_dispo,
                        'color_id':
                        color_num_part_dispo
                    })
                    liste_piece_manquantes_with_color.append({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_set,
                        'color_id':
                        color_id_set
                    })
                    if qty_num_part_dispo > qty_num_part_set:
                        extra_part_num.append({
                            'part_num': num_part_set,
                            'quantity': qty_num_part_dispo - qty_num_part_set,
                            'color_id': color_num_part_dispo
                        })
            else:
                count_without_color += qty_num_part_dispo
                if color_num_part_dispo == color_id_set:
                    count_with_color += qty_num_part_dispo
                    liste_piece_manquantes_with_color.append({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_set - qty_num_part_dispo,
                        'color_id':
                        color_id_set
                    })
                else:
                    liste_piece_manquantes_with_color.append({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_set,
                        'color_id':
                        color_id_set
                    })
                    list_available_part_num_bad_color.append({
                        'part_num':
                        num_part_set,
                        'quantity':
                        qty_num_part_dispo,
                        'color_id':
                        color_id_set
                    })
        #la pièce du set n'est pas dans les pièces dispo.
        #Cette pièce du set est manquante
        else:
            #on récupère l'index de la liste contenant les dictonnaires des
            #part_num nécessaire pour le set, pour lequel le part_num
            #correspond à celui que l'on cherche
            liste_part_num_set = df_set_num.loc[0, 'part_num_qty_color']
            part_num_index = next(
                (index for (index, d) in enumerate(liste_part_num_set)
                 if d["part_num"] == num_part_set), None)
            qty_set = liste_part_num_set[part_num_index]['quantity']
            color_set = liste_part_num_set[part_num_index]['color_id']
            liste_piece_manquantes_with_color.append({
                'part_num': num_part_set,
                'quantity': qty_set,
                'color_id': color_set
            })
    if len(list_infos_part_dispo_fct) > 0:
        extra_part_num.extend(list_infos_part_dispo_fct)

    pourcentage_without_color = round(
        count_without_color / df_set_num['quantity_total_part_num'][0] * 100,
        2)
    pourcentage_with_color = round(
        count_with_color / df_set_num['quantity_total_part_num'][0] * 100, 2)

    return pourcentage_without_color, liste_piece_manquantes_without_color,\
        pourcentage_with_color, liste_piece_manquantes_with_color, \
        list_available_part_num_bad_color, extra_part_num


def ajout_pourcentage_df(liste_parts_disponibles, x, df):
    '''
    fonction appelée par generation_df_ac_pourcentage_pieces_manquantes pour
    ajouter les pourcentages calculés par pourcentage_piece_manquante.
    '''
    return pourcentage_piece_manquante(liste_parts_disponibles, x, df)


def generation_df_ac_pourcentage_pieces_manquantes(liste_parts_disponibles,
                                                   df):
    '''
    Fonction modifiant la dataframe pour ajouter les pourcentages et les
    listes des pièces manquantes ou en plus dans des nouvelles colonnes
    INPUT :
        liste_parts_disponibles: dictionnaire au format :
        liste_parts_disponibles = [
                            {
                                'part_num': '2343',
                                'quantity': 1,
                                'color_id': 45
                            },
                            {...},...
        ]
        df: dataframe listant les sets utilisant au moins une des pièces
        disponibles, résultat de la fonction :
        list_set_contenant_au_moins_une_des_pieces
    OUTPUT :
        dataframe modifiée
    '''
    df['pourcentage_without_color'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[0])
    df['missing_part_num_without_color'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[1])

    df['pourcentage_with_color'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[2])
    df['missing_part_num_with_color'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[3])

    df['available_part_num_bad_color'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[4])
    df['extra_part'] = df['inventory_id'].apply(
        lambda x: ajout_pourcentage_df(liste_parts_disponibles, x, df)[5])
    return df


# Chargement csv
#table principale
csv_path_inventories = 'inventories.csv'

#premier niveau
csv_path_sets = 'csv_rebrickable/sets.csv'
csv_path_inventory_parts_1 = 'csv_rebrickable/inventory_parts_1.csv'
csv_path_inventory_parts_2 = 'csv_rebrickable/inventory_parts_2.csv'
csv_path_inventory_minifigs = 'csv_rebrickable/inventory_minifigs.csv'

#deuxième niveau
#pour set
csv_path_themes = 'csv_rebrickable/themes.csv'
#pour inventory_part
csv_path_parts = 'csv_rebrickable/parts.csv'
#pour inventory_minifigs
csv_path_minifigs = 'csv_rebrickable/minifigs.csv'

#creations dataframes
df_inventories = pd.read_csv(csv_path_inventories)

df_sets = pd.read_csv(csv_path_sets)
df_inventory_parts_1 = pd.read_csv(csv_path_inventory_parts_1)
df_inventory_parts_2 = pd.read_csv(csv_path_inventory_parts_2)
df_inventory_parts = pd.concat([df_inventory_parts_1, df_inventory_parts_2],
                               axis='rows').reset_index(drop=True)

df_inventory_minifigs = pd.read_csv(csv_path_inventory_minifigs)

df_themes = pd.read_csv(csv_path_themes)
df_parts = pd.read_csv(csv_path_parts)
df_minifigs = pd.read_csv(csv_path_minifigs)

if __name__ == "__main__":
    generation_df_ac_pourcentage_pieces_manquantes()
