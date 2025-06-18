import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
from io import BytesIO


def hex_to_rgb(hex_color):
    """Convertit une couleur hexadécimale (ex: '720E0F') en tuple RGB."""
    hex_color = hex_color.strip().lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_tuple):
    """Convertit un tuple RGB en code hexadécimal (ex: (114, 14, 15) → '#720e0f')."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb_tuple)


def load_lego_colors(csv_path):
    """Charge les couleurs LEGO depuis un fichier CSV au format officiel."""
    df = pd.read_csv(csv_path, sep=";")
    df = df[df['RGB'].notna()]
    df['RGB'] = df['RGB'].apply(hex_to_rgb)
    return df[["Name", "RGB"]]


def extract_dominant_color(image_bytes, n_clusters=3):
    """Retourne la couleur dominante d'une image (donnée en bytes)."""
    image = Image.open(image_bytes).convert("RGB")
    image = image.resize((100, 100))  # Réduction pour rapidité
    pixels = np.array(image).reshape(-1, 3)

    # Optionnel : éliminer pixels trop noirs/blancs
    pixels = pixels[(pixels[:, 0] > 20) | (
        pixels[:, 1] > 20) | (pixels[:, 2] > 20)]

    kmeans = KMeans(n_clusters=n_clusters, n_init="auto")
    kmeans.fit(pixels)
    counts = np.bincount(kmeans.labels_)
    dominant_color = kmeans.cluster_centers_[np.argmax(counts)]

    print(tuple(int(c) for c in dominant_color))

    return tuple(int(c) for c in dominant_color)


def find_nearest_lego_color(rgb_color, lego_colors):
    """Retourne la couleur LEGO la plus proche de la couleur donnée."""
    lego_colors["distance"] = lego_colors["RGB"].apply(
        lambda c: np.linalg.norm(np.array(c) - np.array(rgb_color))
    )
    closest = lego_colors.loc[lego_colors["distance"].idxmin()]
    return closest["Name"], rgb_to_hex(closest["RGB"])


def detect_lego_color(image_data, lego_colors):
    """
    Pipeline complet : image en BytesIO ou bytes -> couleur LEGO (nom + hex).
    Accepte un objet BytesIO ou bytes bruts.
    """
    dominant_rgb = extract_dominant_color(image_data)
    name, hex_code = find_nearest_lego_color(dominant_rgb, lego_colors)
    return name, hex_code


# Variable globale qui contiendra la table des couleurs chargée une fois
LEGO_COLORS = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Détecteur de couleur LEGO à partir d'une image.")
    parser.add_argument(
        "image", help="Chemin vers l'image de la pièce LEGO (JPEG/PNG)")
    parser.add_argument(
        "csv", help="Chemin vers le fichier CSV des couleurs LEGO")

    args = parser.parse_args()

    # Chargement unique du CSV
    LEGO_COLORS = load_lego_colors(args.csv)

    with open(args.image, "rb") as f:
        image_data = f.read()

    name, hex_code = detect_lego_color(image_data)
    print(f"Couleur LEGO détectée : {name} ({hex_code})")
