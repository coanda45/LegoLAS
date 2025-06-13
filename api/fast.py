import requests
import os
import pandas as pd
import base64
import warnings

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from dotenv import load_dotenv

from base64 import b64encode, b64decode

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import cv2

from legolas.segmentation.registry import load_model_RF, load_SAM
from legolas.classification.main import classify_part
from legolas.segmentation.constants import RESIZE_VALUES, SAM_CONFIG_1, IMG_08_SIZE, ROBOFLOW_PROJECT_ID_LOD, ROBOFLOW_PROJECT_VERSION_LOD, ROBOFLOW_PROJECT_ID_LBD, ROBOFLOW_PROJECT_VERSION_LBD
from legolas.API_rebrickable.main_api import part_colors
from scripts.utils import resize_SAM_masks

load_dotenv(dotenv_path="../.env", override=True)

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
# BRICKOGNIZE_URL = os.getenv("BRICKOGNIZE_URL")


class PostPredictData(BaseModel):
    """Class for objects used in segmentation"""
    img_base64: str
    model: str


app = FastAPI()
model_LOD = load_model_RF(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_ID_LOD,
                          ROBOFLOW_PROJECT_VERSION_LOD)
model_LBD = load_model_RF(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_ID_LBD,
                          ROBOFLOW_PROJECT_VERSION_LBD)
model_SAM = load_SAM()

assert model_LOD is not None
assert model_LBD is not None
assert model_SAM is not None
app.state.model_LOD = model_LOD
app.state.model_LBD = model_LBD
app.state.model_SAM = model_SAM

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Endpoint for https://your-domain.com/
@app.get("/")
def root():
    return {'message': "Welcome traveler. How did you end up here?"}


# Endpoint for https://your-domain.com/predict?input_one=69&input_two=420
@app.post("/predict")
def post_predict(data: PostPredictData):
    """From an input image:
    - Resize then segment it (i.e., detect parts)
    - Crop individual parts
    - Call Brickognize on each part
    - Build an HTML table from a df

    Returns:
      a JSONResponse object containing info from Brickognize (and more?)
    """

    temp_image_path = "temp.jpeg"
    with open(temp_image_path, "wb") as tmp_file:
        tmp_file.write(b64decode(data.img_base64))
    image = Image.open(temp_image_path)
    # image.show()  # debug, display img in another window

    if data.model == "LOD":
        result = app.state.model_LOD.predict(temp_image_path,
                                             confidence=40,
                                             overlap=30).json()
        preds = result["predictions"]

    elif data.model == "LBD":
        result = app.state.model_LBD.predict(temp_image_path,
                                             confidence=40,
                                             overlap=30).json()
        preds = result["predictions"]

    elif data.model == "SAM":
        ### TMP ###
        # For the demo day, let's use precomputed results, since a Google Colab CPU computation lasts for 26 minutes :(
        # image_arr = cv2.imread(temp_image_path)
        # image_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2RGB)
        # mask_generator = SamAutomaticMaskGenerator(model=model, **SAM_CONFIG_1)
        # preds = mask_generator.generate(image_arr)  # masks are renamed "preds" for consistency with RF
        shrink_factor = max(IMG_08_SIZE[0] / RESIZE_VALUES[0],
                            IMG_08_SIZE[1] / RESIZE_VALUES[1])
        preds = resize_SAM_masks(shrink_factor)
        ### TMP END ###

    else:
        warnings.warn(
            f"data.model must be either 'LOD', 'LBD' or 'SAM', got '{data.model}'"
        )
        return JSONResponse(content={
            "image": None,
            "results": None
        },
            status_code=555)

    os.remove(temp_image_path)
    image_orig = image.copy()

    draw = ImageDraw.Draw(image)  # draw bboxes and labels on top of this
    results = pd.DataFrame()  # store brickognize outputs here

    for i, pred in enumerate(preds):
        if data.model in ["LOD", "LBD"]:
            # RF models
            x, y = pred["x"], pred["y"]  # coords of the center of the brick
            w, h = pred["width"], pred["height"]
            # Compute bbox coords
            left = int(x - w / 2)
            upper = int(y - h / 2)
            right = int(x + w / 2)
            lower = int(y + h / 2)
            confidence = pred["confidence"]
        else:
            # SAM
            left, upper, w, h = pred["bbox"]
            right = left + w
            lower = upper + h
            confidence = pred["predicted_iou"]

        # Crop on bbox
        cropped = image_orig.crop((left, upper, right, lower))

        # Debug
        # print(f"\n➡️ Brique #{i+1} : upper={upper}, left={left}, w={w}, h={h}")
        # cropped.show(title=f"Brique #{i+1}")  # debug, display each cropped image in a new window

        # Préparer l'image pour Brickognize
        buf = BytesIO()
        cropped.save(buf, format="JPEG")
        buf.seek(0)

        jpeg_bytes = buf.getvalue()
        img_base64 = b64encode(jpeg_bytes).decode('utf-8')

        font = ImageFont.truetype("resources/Roboto_Condensed-Medium.ttf",
                                  size=24)
        draw.rectangle([left, upper, right, lower], outline="black", width=4)
        draw.text((left, upper - 24), f"{i+1}", fill="black", font=font)

        # Envoi à Brickognize
        df = classify_part(buf)

        # Traitement des résultats
        if not df.empty:
            expanded = df['external_sites'].apply(
                lambda x: x[0] if len(x) > 0 else None).apply(pd.Series).drop(
                    columns='name').rename(columns={'url': 'bricklink_url'})

            df = pd.concat([df.drop(columns='external_sites'), expanded],
                           axis=1)
            df.reset_index()
            df.insert(loc=0, column='img_base64', value=img_base64)
            df.insert(loc=0, column='image_num', value=i + 1)
            df['color'] = "White"
            df['keep'] = False
            df.at[0, 'keep'] = True

            def _part_colors(x):
                _results = part_colors(x)
                print(_results.rebrickable_id[0])
                print(_results.color_name.to_list())
                return _results.rebrickable_id[0], _results.color_name.to_list()

            df[["rebrickable_id", "colors"]] = df['id'].apply(
                lambda x: pd.Series(_part_colors(x)))

            # print(df)

            results = pd.concat([results, df], ignore_index=True)

    # print(results)

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    return JSONResponse(
        content={
            "image": b64encode(img_bytes).decode('utf-8'),
            "results": results.to_dict(orient="records")
        })
