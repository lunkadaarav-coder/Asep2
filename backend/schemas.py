"""HealthMitra Scan – Pydantic Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Patient ──────────────────────────────────────────
class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    village: Optional[str] = None
    asha_worker_id: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    blood_group: Optional[str]
    phone: Optional[str]
    village: Optional[str]
    asha_worker_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Medical Report ───────────────────────────────────
class ReportResponse(BaseModel):
    id: int
    patient_id: Optional[int]
    filename: str
    ocr_text: Optional[str]
    explanation_en: Optional[str]
    explanation_hi: Optional[str]
    risk_score: float
    risk_level: Optional[str]
    critical_alerts: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Food Scanner ─────────────────────────────────────
class FoodDetection(BaseModel):
    name: str
    confidence: float
    category: str
    is_safe: bool


class NutritionInfo(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float


class FoodScanResponse(BaseModel):
    detected_foods: List[FoodDetection]
    nutrition: NutritionInfo
    warnings: List[str]
    scan_type: str


# ── Voice AI Doctor ──────────────────────────────────
class VoiceResponse(BaseModel):
    transcript: str
    ai_response: str
    language: str


# ── Risk Predictor ───────────────────────────────────
class VitalsInput(BaseModel):
    age: int
    gender: str
    bmi: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    blood_sugar_fasting: Optional[float] = None
    cholesterol_total: Optional[float] = None
    heart_rate: Optional[int] = None
    smoking: bool = False
    family_history_diabetes: bool = False
    family_history_heart: bool = False
    exercise_minutes_weekly: int = 0


class RiskResult(BaseModel):
    diabetes_risk: float
    heart_risk: float
    diabetes_level: str
    heart_level: str
    recommendations: List[str]


# ── Emergency Alert ──────────────────────────────────
class EmergencyAlert(BaseModel):
    is_emergency: bool
    alerts: List[dict]
    severity: str  # critical, warning, normal


# ── System Status ────────────────────────────────────
class SystemStatusResponse(BaseModel):
    cpu_usage: float
    npu_usage: float
    ram_usage: float
    is_offline: bool
    ollama_status: str
    model_loaded: str
    amd_optimized: bool
