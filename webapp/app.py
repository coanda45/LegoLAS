# Standard library
import sys
import os
import io
import traceback
import json
from base64 import b64encode, b64decode, urlsafe_b64encode

# Third-party
import streamlit as st
import requests
import pandas as pd
from PIL import Image

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        image = resize_image(image, RESIZE_VALUES)  # use a smaller image
        st.image(image, caption="Uploaded image", use_container_width=False)

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

            before_df = st.session_state.edited_df.copy()

            # Appliquer un fond coloré dans la colonne "detected_color"
            def style_color_column(row):
                return [
                    f'background-color: {row["detected_color_rgb"]}' if col == "detected_color" else ''
                    for col in row.index
                ]
            # def color_bg(val):
            #     return f'background-color: {val}'

            styled_df = st.session_state.edited_df.style.apply(
                style_color_column, axis=1)

            if "lego_colors" not in st.session_state:
                # TODO Use API and not local version
                st.session_state.lego_colors = get_all_lego_colors()

            st.session_state.edited_df = st.data_editor(
                styled_df,
                column_config={
                    "bricklink_url": st.column_config.LinkColumn("BrickLink", display_text="View"),
                    "img_url": st.column_config.ImageColumn("From URL"),
                    "img_base64": st.column_config.ImageColumn("From Base64"),
                    "color": st.column_config.SelectboxColumn("Color", options=st.session_state.lego_colors["name"].to_list()),
                    "detected_color_rgb": None
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

                st.write("### Selected Parts:")
                st.dataframe(
                    filtered_df,
                    column_config={
                        "bricklink_url": st.column_config.LinkColumn("BrickLink", display_text="View"),
                        "img_url": st.column_config.ImageColumn("From URL"),
                        "img_base64": st.column_config.ImageColumn("From Base64"),
                        "color": st.column_config.SelectboxColumn("Color", options=st.session_state.lego_colors["name"].to_list()),
                        "detected_color_rgb": None
                    },
                    use_container_width=True,
                    hide_index=True
                )

                parts_list = [
                    {
                        "part_num":
                        row["rebrickable_id"],
                        # TODO put color_id
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

                if st.button("Save on Rebrickable Part List"):
                    st.session_state.save_selected_parts = True

                # Conditional rendering of additional buttons
                if st.session_state.save_selected_parts:
                    print("Saving selected parts to Rebrickable Part List...")
                    params = {
                        "user_name": st.secrets["REBRICKABLE_USER_NAME"],
                        "password": st.secrets["REBRICKABLE_USER_PASSWORD"],
                        "part_list_name": st.secrets["REBRICKABLE_PART_LIST_NAME"],
                        "base64_json_parts_list": base64_json_parts_list
                    }
                    with st.spinner("Calling API..."):
                        response = requests.get(
                            f"{api_base_url}/add_parts_to_username_partlist", params=params)
                        if response.status_code == 200:
                            url = response.json().get("url")
                            print(url)
                            st.markdown(f"[🔗 Open Link]({url})",
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
                            st.write("### Available sets, discarding colour matching:")
                            df_no_color_final = pd.DataFrame(
                                json.loads(
                                    response.json().get("df_no_color_final")))
                            st.dataframe(
                                df_no_color_final,
                                column_config={
                                    "img_url":
                                    st.column_config.ImageColumn(
                                        "From URL", width="large"),
                                },
                                # use_container_width=True,
                                hide_index=True)
                            st.write("### Available sets, taking colour matching into account:")
                            df_color_final = pd.DataFrame(
                                json.loads(response.json().get("df_color_final")))
                            st.dataframe(
                                df_color_final,
                                column_config={
                                    "img_url":
                                    st.column_config.ImageColumn(
                                        "From URL", width="large"),
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
