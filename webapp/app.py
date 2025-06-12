import streamlit as st
from PIL import Image
import io
from base64 import b64encode, b64decode
import requests
import pandas as pd

st.title("Please upload an image with your Lego parts :")

uploaded_file = st.file_uploader("Choose a file", type=[
                                 "png", "jpg", "jpeg", "bmp", "gif"])

if uploaded_file is not None:
    try:
        # Ouvrir l'image avec PIL
        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded image", use_container_width=True)

        # Convertir en JPEG dans un buffer mémoire
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG")
        jpeg_bytes = buf.getvalue()

        # st.write("Image converted to JPEG format")

        # Encoder en base64
        img_base64 = b64encode(jpeg_bytes).decode('utf-8')

        # st.write("base64 image encoding")

        # Afficher une partie de la chaîne base64 (optionnel)
        # st.text_area("Base64 (excerpt)",
        #              value=img_base64[:200] + "...", height=150)

        # URL de l'API (à adapter)
        # api_url = "http://localhost:8000/predict/"
        api_url = "https://legolas-733027877169.europe-west1.run.app/predict"

        if st.button("If you are ready for part recognition, click-me !"):
            payload = {"img_base64": img_base64}
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                st.success("Image sent successfully!")

                data = response.json()

                st.image(b64decode(data["image"]))

                df = pd.DataFrame(data["results"])

                df['img_base64'] = df['img_base64'].apply(
                    lambda b64: f'<img src="data:image/jpeg;base64,{b64}" width="80"/>'
                )

                df['img_url'] = df['img_url'].apply(
                    lambda url: f'<img src="{url}" width="80"/>')

                df['bricklink_url'] = df['bricklink_url'].apply(
                    lambda url: f'<a href="{url}" target="_blank">View on BrickLink</a>'
                )

                html_table = df.to_html(escape=False, index=False)
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.error(
                    f"Erreur API : {response.status_code} {response.text}")

    except Exception as e:
        st.error(f"Error processing image: {e}")
