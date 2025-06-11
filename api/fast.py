import requests
import os
import pandas as pd
import base64

from PIL import Image, ImageDraw
from io import BytesIO

# TODO: Import your package, replace this by explicit imports of what you need
from legolas.segmentation.registry import load_model
from legolas.classification.main import classify_part

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from dotenv import load_dotenv

from base64 import b64encode, b64decode

load_dotenv(dotenv_path="../.env", override=True)


ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_PROJECT_ID = os.getenv("ROBOFLOW_PROJECT_ID")
ROBOFLOW_PROJECT_VERSION = os.getenv("ROBOFLOW_PROJECT_VERSION")

# BRICKOGNIZE_URL = os.getenv("BRICKOGNIZE_URL")


class ImageData(BaseModel):
    img_base64: str


app = FastAPI()
model = load_model(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_ID,
                   ROBOFLOW_PROJECT_VERSION)
assert model is not None
app.state.model = model

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
    return {
        'message': "Hi, The API is running!"
    }

# Endpoint for https://your-domain.com/predict?input_one=154&input_two=199


# with open("./raw_data/thumbnail_IMG_8375.jpg", "rb") as input_file:
#     img_base64 = b64encode(input_file.read()).decode('utf-8')

# print(type(img_base64))


@app.post("/predict")
def post_predict(data: ImageData):
    """_summary_

    Returns:
        _type_: _description_
    """

    temp_image_path = "temp.jpeg"

    with open(temp_image_path, "wb") as tmp_file:
        tmp_file.write(b64decode(data.img_base64))

    image = Image.open(temp_image_path)
    image.show()

    result = app.state.model.predict(
        temp_image_path, confidence=40, overlap=30).json()

    os.remove(temp_image_path)

    # results = []
    results = pd.DataFrame()
    for i, pred in enumerate(result["predictions"]):
        x, y = pred["x"], pred["y"]
        w, h = pred["width"], pred["height"]

        # Roboflow donne les coordonnées du centre de la brique
        # Nous devons calculer les coordonnées du rectangle englobant
        left = int(x - w / 2)
        upper = int(y - h / 2)
        right = int(x + w / 2)
        lower = int(y + h / 2)

        # ✅ Protection contre débordement hors image
        # left = max(0, left)
        # upper = max(0, upper)
        # right = min(image.width, right)
        # lower = min(image.height, lower)

        # 🧱 Découpe
        cropped = image.crop((left, upper, right, lower))

        # 👁️ Affichage de l'image découpée
        print(f"\n➡️ Brique #{i+1} : x={x}, y={y}, w={w}, h={h}")
        # cropped.show(title=f"Brique #{i+1}")
        cropped.show()

        # 📨 Préparer l'image pour Brickognize
        buf = BytesIO()
        cropped.save(buf, format="JPEG")
        buf.seek(0)

        jpeg_bytes = buf.getvalue()
        img_base64 = b64encode(jpeg_bytes).decode('utf-8')

        # 🔗 Envoi à Brickognize
        # files = {
        #     "query_image": (f"lego_{i}.jpg", buf, "image/jpeg")
        # }

        # response = requests.post(
        #     BRICKOGNIZE_URL,
        #     headers={"accept": "application/json"},
        #     files=files
        # )
        # response.raise_for_status()

        # results.append({
        #     "bbox": pred,
        #     "brickognize": response.json()
        # })

        # print(response.json()["items"][0]["name"])
        # url = response.json()["items"][0]["img_url"]

        # response = requests.get(url)
        # img = Image.open(BytesIO(response.content))
        # img.show()
        df = classify_part(buf)

        if not df.empty:
            expanded = df['external_sites'].apply(lambda x: x[0] if len(x) > 0 else None).apply(
                pd.Series).drop(columns='name').rename(columns={'url': 'bricklink_url'})

            df = pd.concat(
                [df.drop(columns='external_sites'), expanded], axis=1)

            df.reset_index()

            df.insert(loc=0, column='img_base64', value=img_base64)

            df.insert(loc=0, column='image_num', value=i+1)

            print(df)

            results = pd.concat([results, df], ignore_index=True)

    print(results)

    draw = ImageDraw.Draw(image)

    for pred in result["predictions"]:
        x, y = pred["x"], pred["y"]
        w, h = pred["width"], pred["height"]
        label = pred["class"]
        confidence = pred["confidence"]

        left = int(x - w / 2)
        upper = int(y - h / 2)
        right = int(x + w / 2)
        lower = int(y + h / 2)

        draw.rectangle([left, upper, right, lower], outline="red", width=2)
        draw.text((left, upper - 10),
                  f"{label} ({confidence:.2f})", fill="red")

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    return JSONResponse(content={
        "image": b64encode(img_bytes).decode('utf-8'),
        "results": results.to_dict(orient="records")
    })
