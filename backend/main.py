import os
import openai
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # You need to set this

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
    return {"message": "Vision-based stylist backend is live!"}

def analyze_image_with_replicate(image_bytes):
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "version": "a1c19b43f8b6cd38f7fc2cdd58c65d9a2cfdb4a79a0e3f9fe0c4298d67c002b8",
            "input": {
                "image": "data:image/jpeg;base64," + image_bytes.decode("utf-8")
            }
        }
    )
    result = response.json()
    return result["prediction"] if "prediction" in result else "a clothing item"

@app.post("/suggest")
async def suggest_outfits(files: List[UploadFile] = File(...)):
    import base64
    descriptions = []

    for file in files:
        image_data = await file.read()
        b64_image = base64.b64encode(image_data)
        desc = analyze_image_with_replicate(b64_image)
        descriptions.append(desc)

    combined_description = "\n".join(f"- {desc}" for desc in descriptions)
    prompt = f"""
You are a professional fashion stylist. I uploaded photos of these clothing items:

{combined_description}

Please suggest 3 stylish outfits using them: one for work, one for casual, one for evening.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative fashion stylist AI."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"outfits": response.choices[0].message.content}
