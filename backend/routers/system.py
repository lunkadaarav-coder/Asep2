"""HealthMitra Scan – System Status Router"""
import random
import platform
from fastapi import APIRouter
from services.llm_service import get_ollama_status

router = APIRouter(prefix="/api/system", tags=["System Status"])


@router.get("/status")
def get_system_status():
    """Get system resource usage and AI model status."""
    ollama = get_ollama_status()

    # Simulate system metrics (in production, use psutil)
    cpu_usage = round(random.uniform(15, 45), 1)
    npu_usage = round(random.uniform(5, 35), 1) if ollama["ollama_running"] else 0
    ram_usage = round(random.uniform(40, 70), 1)

    return {
        "cpu_usage": cpu_usage,
        "npu_usage": npu_usage,
        "ram_usage": ram_usage,
        "is_offline": True,
        "ollama_status": ollama["status"],
        "model_loaded": ollama["model_loaded"],
        "ollama_installed": ollama["ollama_installed"],
        "amd_optimized": True,
        "platform": platform.processor() or "AMD Ryzen AI",
        "python_version": platform.python_version(),
        "os": platform.system()
    }


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "HealthMitra Scan", "version": "1.0.0"}
