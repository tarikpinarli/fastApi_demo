# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from logic import generate_recommendation
from supabase import create_client, Client
import os

# --- Supabase client ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

app = FastAPI()

# --- CORS: allow Figma to call this directly ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    user_id: str
    steps: int
    heart_rate: float

@app.post("/generate-recommendation")
def generate_recommendation_endpoint(data: InputData):
    # 1) run your Python logic
    result = generate_recommendation(
        user_id=data.user_id,
        steps=data.steps,
        heart_rate=data.heart_rate,
    )

    # 2) save to Supabase
    supabase.table("recommendations").insert({
        "user_id": data.user_id,
        "steps": data.steps,
        "heart_rate": data.heart_rate,
        "score": result["score"],
        "recommendation": result["recommendation"],
    }).execute()

    # 3) return to Figma
    return result
