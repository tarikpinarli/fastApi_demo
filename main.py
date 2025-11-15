# main.py

import os
import sqlite3
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "recommendation.db")
PREDICTION_SCRIPT = os.path.join(BASE_DIR, "prediction.py")

# ---------- Supabase client ----------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ---------- FastAPI app ----------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- SQLite helper ----------
SQL_SELECT_LATEST = """
    SELECT recommended_temp, recommended_hum, recommended_duration
    FROM recommendations
    ORDER BY rowid DESC
    LIMIT 1;
"""


def read_latest_from_sqlite():
    """Read latest (temp, hum, duration) from recommendation.db."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(SQL_SELECT_LATEST)
        row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise ValueError("No rows found in recommendations table")

    recommended_temp, recommended_hum, recommended_duration = row
    return recommended_temp, recommended_hum, recommended_duration


# ---------- API Endpoint ----------
@app.post("/generate-recommendation")
def generate_recommendation_endpoint():
    """
    1. Run prediction.py to generate/update recommendation.db
    2. Read latest recommendation from recommendation.db
    3. Insert {temp, humidity, duration} into Supabase
    4. Return same payload as JSON
    """
    # 1) Run prediction.py as a subprocess
    try:
        result = subprocess.run(
            ["python3", PREDICTION_SCRIPT],
            capture_output=True,
            text=True,
            check=True,   # raises CalledProcessError if non-zero exit
        )
        # Optional debug:
        print("prediction.py stdout:", result.stdout)
        if result.stderr:
            print("prediction.py stderr:", result.stderr)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"prediction.py failed: {e.stderr or str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running prediction.py: {e}",
        )

    # 2) Read SQLite DB
    try:
        temp, humidity, duration = read_latest_from_sqlite()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # 3) Build payload
    payload = {
        "temp": temp,
        "humidity": humidity,
        "duration": duration,
    }

    # 4) Insert into Supabase
    try:
        supabase.table("daily_recommendations").insert(payload).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase insert error: {e}")

    # 5) Return payload to caller (Figma / Make)
    return payload
