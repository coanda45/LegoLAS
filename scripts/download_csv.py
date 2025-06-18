import datetime
import os
import pandas as pd
from urllib import request
import re


def purge(dir: str, pattern: str):
    '''
    Efface tous les fichiers contenus dans le dossier dir s'il respect le pattern
    '''
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def download_csv_elements() -> pd.DataFrame:
    '''
    Récupère les csv du jour s'il ne sont pas déjà présents dans le dossier
    tmp. Si les fichiers présents sont ceux de jours passés, on les efface
    et on les remplace par les gz du jour.
    On les unzip et au final on créé les dataframe.
    '''
    # récupération des csv
    # url
    elements_path = 'https://cdn.rebrickable.com/media/downloads/elements.csv.gz'

    # date du jour
    today = datetime.date.today()
    today_f = datetime.datetime.strftime(today, '%y%m%d')

    # on récupère les noms des fichiers
    elements_name = re.split(pattern='/', string=elements_path)[-1]

    # ajout today date aux noms des ficheirs gz
    elements_dated_name = elements_name[:-3] + "_" + today_f + '.gz'

    # liens de sauvegarde des gz renommés
    tmp_dir = '/tmp'  # os.path.dirname(__file__) +
    file_elements_path = f'{tmp_dir}/{elements_dated_name}'

    # si les fichier gz datés du jour existent déjà, on ne les retélécharge pas.
    # sinon, on efface l'ancien gz et les csv unzippés.
    if not os.path.isfile(file_elements_path):
        # s'il n'existe pas, on efface l'ancien fichier csv et gz
        # s'il existe, on ne fait rien (on ne redl pas et on ne dezip pas)
        dir = os.listdir(tmp_dir)
        # Checking if the list is empty or not
        if len(dir) > 0:
            purge(tmp_dir, '/elements.csv')

        request.urlretrieve(url=elements_path,
                            filename=file_elements_path)

    # creations dataframes
    df_elements = pd.read_csv(file_elements_path,
                              compression='gzip',
                              header=0,
                              sep=',',
                              on_bad_lines='skip')

    return df_elements[["part_num", "color_id"]]


if __name__ == "__main__":
    df = download_csv_elements()
    print(df.head())
