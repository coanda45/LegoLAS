import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json

# Set layout to wide
st.set_page_config(layout="wide")
st.title("🧱 LEGO Part Annotator – Add Bounding Boxes")

# Upload an image
uploaded_file = st.file_uploader(
    "📤 Upload a LEGO image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load the image and convert to RGBA
    image = Image.open(uploaded_file).convert("RGBA")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Use PIL image in canvas
    st.subheader("✏️ Draw bounding boxes on the image")
    canvas_result = st_canvas(
        fill_color="rgba(0, 255, 0, 0.3)",  # Transparent fill
        stroke_width=3,
        stroke_color="#00FF00",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="rect",
        key="canvas",
    )

    # Process drawn objects
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        boxes = []

        for obj in objects:
            box = {
                "label": obj.get("name", "lego_part"),
                "x": int(obj["left"]),
                "y": int(obj["top"]),
                "width": int(obj["width"]),
                "height": int(obj["height"]),
            }
            boxes.append(box)

        st.subheader("📦 Extracted Bounding Boxes")
        st.json(boxes)

        # JSON export
        json_export = json.dumps(boxes, indent=4)
        st.download_button(
            label="💾 Download as JSON",
            data=json_export,
            file_name="bounding_boxes.json",
            mime="application/json"
        )
