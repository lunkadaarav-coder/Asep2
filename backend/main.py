"""HealthMitra Scan – FastAPI Application Entry Point"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db
from config import APP_NAME, APP_VERSION, CORS_ORIGINS, UPLOAD_DIR

from routers import reports, food, voice, risk, patients, system, dashboard, health_twin, meal
from routers import auth
from services.meal_classifier import load_meal_model

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered offline health assistant for rural India"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files – serve uploads including profile photos
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(food.router)
app.include_router(voice.router)
app.include_router(risk.router)
app.include_router(patients.router)
app.include_router(system.router)
app.include_router(dashboard.router)
app.include_router(health_twin.router)
app.include_router(meal.router)


@app.on_event("startup")
async def startup():
    init_db()
    try:
        load_meal_model()
        print("🍽️ Meal classifier loaded")
    except Exception as e:
        print(f"⚠️ Meal classifier unavailable: {e}")
    print(f"\n🏥 {APP_NAME} v{APP_VERSION}")
    print(f"📂 Upload directory: {UPLOAD_DIR}")
    print(f"🔗 API docs: http://localhost:8000/docs")


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "endpoints": {
            "auth": "/api/auth",
            "reports": "/api/reports",
            "food": "/api/food",
            "voice": "/api/voice",
            "risk": "/api/risk",
            "patients": "/api/patients",
            "system": "/api/system",
            "meal_scanner": "/api/scan-meal",
        }
    }


if __name__ == "__main__":
    import uvicorn
    # Keep direct execution stable across environments by avoiding the
    # autoreloader subprocess. Use `uvicorn main:app --reload` during local
    # development when hot-reload is explicitly needed.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
