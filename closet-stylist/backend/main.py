
import os
import openai
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

openai.api_key = os.getenv("OPENAI_API_KEY")

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
    return {"message": "Closet Stylist backend is live!"}

@app.post("/suggest")
async def suggest_outfits(files: List[UploadFile] = File(...)):
    filenames = ", ".join([file.filename for file in files])
    prompt = f"I uploaded these clothes: {filenames}. Suggest 5 stylish outfits using these pieces for work, casual, and evening settings."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a personal stylist AI."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"outfits": response['choices'][0]['message']['content']}
