import streamlit as st
from PIL import Image
import io
from base64 import b64encode, b64decode
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("Please upload an image with your Lego parts :")

uploaded_file = st.file_uploader("Choose a file", type=[
                                 "png", "jpg", "jpeg", "bmp", "gif"])

lego_colors = pd.read_csv("./webapp/Lego_Colors.csv",
                          delimiter=';', encoding='utf-8')

if uploaded_file:
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

        # Only call the API once
        if "api_data" not in st.session_state:
            api_url = st.secrets["API_URL"]
            payload = {"img_base64": img_base64}
            with st.spinner("Calling API..."):
                response = requests.post(api_url, json=payload)
                if response.status_code == 200:
                    st.session_state.api_data = response.json()
                    data = st.session_state.api_data
                    df = pd.DataFrame(data["results"])
                else:
                    st.error("API call failed")
                    st.stop()

        # Use cached result
        st.image(b64decode(st.session_state.api_data["image"]))

        # Store edited version in session_state
        if "edited_df" not in st.session_state:
            st.session_state.edited_df = df.copy()
            # print(type(st.session_state.edited_df))
            st.session_state.edited_df["img_base64"] = st.session_state.edited_df["img_base64"].apply(
                lambda b64: f"data:image/jpeg;base64,{b64}")

        edited_df = st.session_state.edited_df

        # print(type(st.session_state.edited_df))

        before_df = st.session_state.edited_df.copy()

        edited_df = st.data_editor(
            edited_df,
            column_config={
                "keep": st.column_config.CheckboxColumn("Keep this part?"),
                "bricklink_url": st.column_config.LinkColumn("BrickLink", display_text="View"),
                "img_url": st.column_config.ImageColumn("From URL"),
                "img_base64": st.column_config.ImageColumn("From Base64"),
                "color": st.column_config.SelectboxColumn("Color", options=lego_colors["Name"].to_list()),
            },
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="changes"
        )

        st.session_state.edited_df = edited_df
        # print(before_df.head())
        # print(edited_df.head())
        # print(before_df.compare(edited_df))
        if not before_df.equals(edited_df):
            st.rerun()

    except Exception as e:
        st.error(f"Error processing image: {e}")
