"""HealthMitra Scan – Food Scanner Router"""
import os
import json
import logging
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import FoodScan, HealthTimeline
from services.food_detector import detect_food
from config import UPLOAD_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/food", tags=["Food Scanner"])

_pool = ThreadPoolExecutor(max_workers=2)


@router.post("/scan")
async def scan_food(
    file: UploadFile = File(...),
    patient_id: int = Form(None),
    scan_type: str = Form("single"),
):
    """Scan food image using YOLOv8 to detect Indian food items and nutrition."""
    try:
        file_path = os.path.join(UPLOAD_DIR, f"food_{file.filename}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_pool, detect_food, file_path, scan_type)

        db = SessionLocal()
        try:
            scan = FoodScan(
                patient_id=patient_id,
                image_path=file_path,
                detected_foods=json.dumps(result["detected_foods"]),
                nutrition_info=json.dumps(result["nutrition"]),
                warnings=json.dumps(result["warnings"]),
                scan_type=scan_type
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)

            food_names = ", ".join([f["name"] for f in result["detected_foods"]])
            timeline_entry = HealthTimeline(
                patient_id=patient_id,
                event_type="scan",
                title=f"Food Scan: {food_names}",
                description=f"Total calories: {result['nutrition']['calories']} kcal",
                data_json=json.dumps({"scan_id": scan.id})
            )
            db.add(timeline_entry)
            db.commit()
        finally:
            db.close()

        return result

    except Exception as e:
        logger.error(f"Food scan failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Food scan failed: {str(e)}")


@router.post("/meal")
async def scan_meal(
    file: UploadFile = File(...),
    patient_id: int = Form(None),
):
    """Scan a meal plate to detect multiple food items and analyze the full meal."""
    try:
        file_path = os.path.join(UPLOAD_DIR, f"meal_{file.filename}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_pool, detect_food, file_path, "meal")

        safe_foods = [f for f in result["detected_foods"] if f["is_safe"]]
        unsafe_foods = [f for f in result["detected_foods"] if not f["is_safe"]]

        db = SessionLocal()
        try:
            scan = FoodScan(
                patient_id=patient_id,
                image_path=file_path,
                detected_foods=json.dumps(result["detected_foods"]),
                nutrition_info=json.dumps(result["nutrition"]),
                warnings=json.dumps(result["warnings"]),
                scan_type="meal"
            )
            db.add(scan)
            db.commit()
        finally:
            db.close()

        return {
            **result,
            "safe_foods": safe_foods,
            "unsafe_foods": unsafe_foods,
            "meal_score": round((len(safe_foods) / max(len(result["detected_foods"]), 1)) * 100)
        }

    except Exception as e:
        logger.error(f"Meal scan failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Meal scan failed: {str(e)}")


@router.get("/history")
def get_food_history(patient_id: int = None, db: Session = Depends(get_db)):
    """Get food scan history."""
    query = db.query(FoodScan)
    if patient_id:
        query = query.filter(FoodScan.patient_id == patient_id)
    scans = query.order_by(FoodScan.created_at.desc()).limit(30).all()

    return [{
        "id": s.id,
        "detected_foods": json.loads(s.detected_foods) if s.detected_foods else [],
        "nutrition_info": json.loads(s.nutrition_info) if s.nutrition_info else {},
        "scan_type": s.scan_type,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in scans]
