"""Meal scanner router backed by EfficientNet-B4 classifier."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import MedicalReport
from services.food_detector import detect_food
from services.meal_classifier import classify_meal_image, ensure_model_ready

router = APIRouter(tags=["Meal Scanner"])


def _extract_numeric_profile(report_payload: dict) -> dict[str, float]:
    profile: dict[str, float] = {}

    candidates = report_payload.get("parameters") or report_payload.get("extracted_parameters") or []
    for item in candidates:
        parameter = str(item.get("parameter") or item.get("name") or "").strip().lower()
        raw_value = item.get("value")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue

        if "hba1c" in parameter or "a1c" in parameter:
            profile["hba1c"] = value
        elif "ldl" in parameter:
            profile["ldl"] = value
        elif "triglyceride" in parameter or parameter == "tg" or "triglycerides" in parameter:
            profile["triglycerides"] = value

    return profile


def _get_patient_profile(db: Session, patient_id: int | None) -> dict[str, float] | None:
    if patient_id is None:
        return None

    report = (
        db.query(MedicalReport)
        .filter((MedicalReport.patient_id == patient_id) | (MedicalReport.user_id == patient_id))
        .order_by(MedicalReport.created_at.desc())
        .first()
    )
    if not report or not report.structured_data:
        return None

    try:
        payload = json.loads(report.structured_data)
    except json.JSONDecodeError:
        return None

    profile = _extract_numeric_profile(payload)
    return profile or None


def _fallback_from_food_detector(image_path: str) -> dict:
    detection = detect_food(image_path, "meal")
    foods = detection.get("detected_foods") or []
    if not foods:
        raise RuntimeError("Meal classifier unavailable and fallback detector found no foods")

    sorted_foods = sorted(foods, key=lambda f: float(f.get("confidence", 0)), reverse=True)
    generic_labels = {"food_bowl", "bowl", "cup", "chai_/_beverage", "beverage"}

    normalized = []
    for item in sorted_foods:
        cleaned = str(item.get("name", "unknown")).split("(")[0].strip().lower().replace(" ", "_").replace("/", "_")
        normalized.append({
            "label": cleaned,
            "confidence": round(float(item.get("confidence", 0)) * 100, 2),
        })

    non_generic = [row for row in normalized if row["label"] not in generic_labels]
    ranked = non_generic if non_generic else normalized
    top_3 = [
        {"label": item["label"], "confidence": item["confidence"]}
        for item in ranked[:3]
    ]

    predicted_food = top_3[0]["label"]
    confidence = top_3[0]["confidence"]

    if predicted_food in generic_labels:
        return {
            "predicted_food": "unknown_food",
            "confidence": confidence,
            "top_3": top_3,
            "status": "Uncertain",
            "fallback": "food_detector",
            "message": "Exact dish could not be identified without the meal classification model.",
        }

    return {
        "predicted_food": predicted_food,
        "confidence": confidence,
        "top_3": top_3,
        "status": "Confident" if confidence >= 60 else "Uncertain",
        "fallback": "food_detector",
    }


@router.post("/api/scan-meal")
async def scan_meal(
    file: UploadFile | None = File(default=None),
    patient_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    if file is None:
        raise HTTPException(status_code=400, detail="Empty request: file is required")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty request: uploaded file has no name")

    suffix = Path(file.filename).suffix or ".jpg"
    temp_path = None
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Corrupt upload: empty file content")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(content)
            temp_path = tmp_file.name

        patient_profile = _get_patient_profile(db, patient_id)

        try:
            ensure_model_ready()
            return classify_meal_image(temp_path, patient_profile=patient_profile)
        except Exception:
            return _fallback_from_food_detector(temp_path)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Meal scan failed: {exc}") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
