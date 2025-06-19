import requests
import pandas as pd
import os

from streamlit import secrets

REBRICKABLE_API_KEY = secrets["REBRICKABLE_API_KEY"]


def get_all_lego_colors() -> pd.DataFrame:
    """
    Fetches all LEGO colors from the Rebrickable API and returns a DataFrame.

    Parameters:

    Returns:
        pd.DataFrame: DataFrame containing all LEGO color details.
    """
    url = "https://rebrickable.com/api/v3/lego/colors/"
    headers = {
        "Authorization": f"key {REBRICKABLE_API_KEY}"
    }

    all_colors = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch data: {response.status_code}\n{response.text}")

        data = response.json()
        all_colors.extend(data['results'])
        url = data.get('next')  # follow pagination if present

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(all_colors)
    df["id"] = pd.to_numeric(df["id"], downcast="integer")
    return df


if __name__ == "__main__":
    df = get_all_lego_colors()
    print(df.info())
    print(df.query("name == 'Glitter Milky White'")['id'].values[0])
