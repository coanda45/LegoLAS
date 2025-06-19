# Standard library
import io
import traceback
import json
from base64 import b64encode, b64decode, urlsafe_b64encode

# Third-party
import streamlit as st
import requests
import pandas as pd
from PIL import Image

# Local application
from legolas.segmentation.constants import RESIZE_VALUES
from scripts.utils import resize_image
# TODO Use API and not local version
from scripts.lego_colors import get_all_lego_colors

st.set_page_config(layout="wide")

st.title("Please upload an image with your LEGO parts:")
uploaded_file = st.file_uploader("Choose a file",
                                 type=["png", "jpg", "jpeg", "bmp", "gif"])

api_base_url = st.secrets["API_BASE_URL"]

table_max_height = 555
line_height  = 36

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        image = resize_image(image, RESIZE_VALUES)  # use a smaller image
        st.image(image, caption="Uploaded image")

        # Convertir en JPEG dans un buffer mémoire
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG")
        jpeg_bytes = buf.getvalue()

        # Encoder en base64
        img_base64 = b64encode(jpeg_bytes).decode('utf-8')

        # Only call the API once
        if "api_data" not in st.session_state:
            model_options = {
                "-": None,
                "(Roboflow Lego Object Detection) Quick and dirty": "LOD",
                "(Roboflow Lego Brick Detector) Quick and not so dirty": "LBD",
                "(Meta Segment Anything Model) Slow but comprehensive (hopefully)": "SAM"
            }
            selected_label = st.selectbox("Choose a model for part detection:",
                                          list(model_options.keys()),
                                          accept_new_options=False)
            model_name = model_options[selected_label]
            is_model_chosen = model_name is not None

            if is_model_chosen:
                payload = {"img_base64": img_base64, "model": model_name}
                with st.spinner("Calling API..."):
                    response = requests.post(
                        f"{api_base_url}/predict", json=payload)
                    if response.status_code == 200:
                        st.session_state.api_data = response.json()
                        data = st.session_state.api_data
                        df = pd.DataFrame(data["results"])
                        # print(f"API response:\n{json.dumps(data, indent=2)}")
                        if df.shape[0] == 0:
                            st.error(
                                "No part found on the image. Please try another model"
                            )
                            st.stop()
                    elif response.status_code == 555:
                        st.error(
                            "Error recovering brick dataframe. Double-check the name of the segmentation model"
                        )
                        st.stop()
                    else:
                        st.error("API call failed")
                        st.stop()
            else:
                df = pd.DataFrame({})

        # Use cached result
        if "api_data" in st.session_state:
            st.image(b64decode(st.session_state.api_data["image"]),
                     caption="Segmented image")

        # Store edited version in session_state
        if "edited_df" not in st.session_state:
            if "img_base64" in df.columns:
                st.session_state.edited_df = df.copy()
                # print(type(st.session_state.edited_df))
                st.session_state.edited_df[
                    "img_base64"] = st.session_state.edited_df[
                        "img_base64"].apply(
                            lambda b64: f"data:image/jpeg;base64,{b64}")
            else:
                # IDK how to handle this lmao good luck
                pass

        if "edited_df" in st.session_state:
            # print(type(st.session_state.edited_df))
            st.write("### Detected parts:")
            before_df = st.session_state.edited_df.copy()

            # Appliquer un fond coloré dans la colonne "detected_color"
            def style_color_column(row):
                return [
                    f'background-color: {row["detected_color_rgb"]}' if col == "detected_color" else ''
                    for col in row.index
                ]

            styled_df = st.session_state.edited_df.style.apply(
                style_color_column, axis=1)

            if "lego_colors" not in st.session_state:
                # TODO Use API and not local version
                st.session_state.lego_colors = get_all_lego_colors()

            height = min(table_max_height, line_height * (len(st.session_state.edited_df) + 1))  # 36 px per line but no more than 555 px
            st.session_state.edited_df = st.data_editor(
                styled_df,
                height=height,
                column_config={
                    "image_num": st.column_config.NumberColumn("Crop ID"),
                    "img_base64": st.column_config.ImageColumn("Crop image"),
                    "id": st.column_config.NumberColumn("Bricklink ID"),
                    "name": st.column_config.TextColumn("Bricklink name"),
                    "img_url": st.column_config.ImageColumn("Bricklink image"),
                    "category": st.column_config.TextColumn("Bricklink category"),
                    "type" : None,
                    "score": st.column_config.NumberColumn("Confidence (%)", format="%.3f"),
                    "bricklink_url": st.column_config.LinkColumn("Bricklink page", display_text="View"),
                    "quantity": st.column_config.NumberColumn("Quantity"),
                    "detected_color": st.column_config.ImageColumn("Detected color"),
                    "color": st.column_config.SelectboxColumn("Color", options=st.session_state.lego_colors["name"].to_list()),
                    "detected_color_rgb": None,
                    "rebrickable_id": st.column_config.NumberColumn("Rebrickable ID"),
                    # "colors": st.column_config.TextColumn("Available colors", disabled=True),
                },
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                key="changes",
                disabled=["detected_color"],
            )

            # print(before_df.head())
            # print(st.session_state.edited_df.head())
            # print(before_df.compare(edited_df))
            if not before_df.equals(st.session_state.edited_df):
                st.rerun()

            # Initialize unlock flag in session_state
            if 'show_selected_parts' not in st.session_state:
                st.session_state.show_selected_parts = False

            if st.button("Show Selected Parts"):
                st.session_state.show_selected_parts = True

            if st.session_state.show_selected_parts:
                filtered_df = st.session_state.edited_df[
                    (st.session_state.edited_df["quantity"] != 0) & (
                        st.session_state.edited_df["rebrickable_id"].notna())
                ]
                agg_dict = {col: 'first' for col in filtered_df.columns if col not in [
                    'id', 'color', 'quantity']}
                agg_dict['quantity'] = 'sum'
                filtered_df = filtered_df.groupby(
                    ['id', 'color'], as_index=False).agg(agg_dict)
                height = min(table_max_height, line_height * (len(st.session_state.edited_df) + 1))
                st.write("### Selected parts:")
                st.dataframe(
                    filtered_df,
                    column_config={
                        "id": st.column_config.NumberColumn("Bricklink ID"),
                        "color": st.column_config.SelectboxColumn("Color", options=st.session_state.lego_colors["name"].to_list()),
                        "image_num": st.column_config.NumberColumn("Crop ID"),
                        "img_base64": st.column_config.ImageColumn("Crop image"),
                        "name": st.column_config.TextColumn("Bricklink name"),
                        "img_url": st.column_config.ImageColumn("Bricklink image"),
                        "category": st.column_config.TextColumn("Bricklink category"),
                        "type" : None,
                        "score": st.column_config.NumberColumn("Confidence (%)", format="%.3f"),
                        "bricklink_url": st.column_config.LinkColumn("Bricklink page", display_text="View"),
                        "detected_color": st.column_config.ImageColumn("Detected color"),
                        "detected_color_rgb": None,
                        "rebrickable_id": st.column_config.NumberColumn("Rebrickable ID"),
                        "quantity": st.column_config.NumberColumn("Quantity"),
                    },
                    use_container_width=True,
                    hide_index=True
                )

                parts_list = [
                    {
                        "part_num":
                        row["rebrickable_id"],
                        "color_id":
                        st.session_state.lego_colors.query(
                            f"name == @row['color']")['id'].values[0].item(),
                        "quantity":
                            row["quantity"]
                    } for _, row in filtered_df.iterrows()
                ]
                # print(parts_list)
                json_parts_list = json.dumps(parts_list)
                # print(json_parts_list)
                base64_json_parts_list = urlsafe_b64encode(
                    json_parts_list.encode()).decode()
                # print(base64_json_parts_list)

                # Initialize unlock flag in session_state
                if 'save_selected_parts' not in st.session_state:
                    st.session_state.save_selected_parts = False

                if "show_form" not in st.session_state:
                    st.session_state.show_form = False

                if st.button("Save part list to Rebrickable"):
                    st.session_state.show_form = True

                if st.session_state.show_form:
                    st.subheader("Rebrickable authentication:")
                    st.text("Please authenticate to Rebrickable in order to save your part list.")
                    st.text("Entering a new part list will create it. Entering an existing one will expand it.")
                    with st.form("rebrickable_authentication"):
                        username = st.text_input("Username", type="default")
                        password = st.text_input("Password", type="password")
                        part_list_name = st.text_input("Part list name", type="default")

                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            st.session_state.show_form = False
                            params = {
                                "user_name": username,
                                "password": password,
                                "part_list_name": part_list_name,
                                "base64_json_parts_list": base64_json_parts_list
                            }

                            with st.spinner("Calling API..."):
                                response = requests.get(
                                    f"{api_base_url}/add_parts_to_username_partlist", params=params)
                                if response.status_code == 200:
                                    url = response.json().get("url")
                                    print(url)
                                    st.markdown(f"[See part list on Rebrickable]({url})",
                                                unsafe_allow_html=True)
                                    st.session_state.save_selected_parts = False
                                else:
                                    st.error("API call failed")
                                    st.stop()

                # Initialize unlock flag in session_state
                if 'show_suggested_sets' not in st.session_state:
                    st.session_state.show_suggested_sets = False

                if st.button("Suggest sets to build"):
                    st.session_state.show_suggested_sets = True

                # Conditional rendering of additional buttons
                if st.session_state.show_suggested_sets:
                    print("Suggest sets to build with or without set colors...")
                    params = {"base64_json_parts_list": base64_json_parts_list}
                    with st.spinner("Calling API..."):
                        response = requests.get(
                            f"{api_base_url}/generate_final_df", params=params)
                        if response.status_code == 200:
                            print(type(response.json().get("df_no_color_final")))
                            st.write("### Available sets, discarding colour matching:")
                            df_no_color_final = pd.DataFrame(
                                json.loads(
                                    response.json().get("df_no_color_final")))
                            st.dataframe(
                                df_no_color_final,
                                column_config={
                                    "inventory_id": st.column_config.NumberColumn("Inventory ID"),
                                    "img_url": st.column_config.ImageColumn("Set image", width="large"),
                                    "set_num": st.column_config.TextColumn("Set ID"),
                                    "percent_no_colour": st.column_config.NumberColumn("Available parts (%)"),
                                },
                                # use_container_width=True,
                                hide_index=True)
                            print(type(response.json().get("df_color_final")))
                            st.write("### Available sets, taking colour matching into account:")
                            df_color_final = pd.DataFrame(
                                json.loads(response.json().get("df_color_final")))
                            st.dataframe(
                                df_color_final,
                                column_config={
                                    "inventory_id": st.column_config.NumberColumn("Inventory ID"),
                                    "img_url": st.column_config.ImageColumn("Set image"),
                                    "set_num": st.column_config.TextColumn("Set ID"),
                                    "percent_colour_match": st.column_config.NumberColumn("Available parts (%)"),
                                },
                                # use_container_width=True,
                                hide_index=True)
                            st.session_state.show_suggested_sets = False
                        else:
                            st.error("API call failed")
                            st.stop()

    except Exception as e:
        st.error(f"Error processing image: {e}")
        traceback_str = traceback.format_exc()
        print(traceback_str)
