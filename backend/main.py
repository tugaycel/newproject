import os
import openai
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import base64
from PIL import Image
import io

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Vision stylist with collage backend is live!"}

def analyze_image_with_replicate(image_bytes):
    try:
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "version": "db21e45e09e5c62f8188f2c5ccf6d2e3f26b8f3e6b85f9be58e183442b16438c",
                "input": {
                    "image": "data:image/jpeg;base64," + image_bytes.decode("utf-8")
                }
            }
        )
        result = response.json()
        return result.get("prediction", "an unknown clothing item")
    except Exception as e:
        return f"a clothing item (description failed: {e})"

def create_collage(images: List[bytes]) -> str:
    pil_images = [Image.open(io.BytesIO(img)).convert("RGB") for img in images]
    widths, heights = zip(*(img.size for img in pil_images))
    total_width = sum(widths)
    max_height = max(heights)

    collage = Image.new("RGB", (total_width, max_height))
    x_offset = 0
    for img in pil_images:
        collage.paste(img, (x_offset, 0))
        x_offset += img.width

    buffer = io.BytesIO()
    collage.save(buffer, format="JPEG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_image

@app.post("/suggest")
async def suggest_outfits(files: List[UploadFile] = File(...)):
    descriptions = []
    image_data_list = []

    for file in files:
        image_data = await file.read()
        image_data_list.append(image_data)
        b64_image = base64.b64encode(image_data)
        desc = analyze_image_with_replicate(b64_image)
        descriptions.append(desc)

    combined_description = "\n".join(f"- {desc}" for desc in descriptions)
    prompt = f"""
You are a professional fashion stylist. The user uploaded these clothing items:

{combined_description}

Using all of them together, suggest 3 complete and stylish outfits: one for work, one for casual, and one for evening. Be creative and practical in combining the items.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional fashion stylist."},
            {"role": "user", "content": prompt}
        ]
    )

    collage_base64 = create_collage(image_data_list)

    return {
        "outfits": response.choices[0].message.content,
        "collage_image_base64": collage_base64
    }
