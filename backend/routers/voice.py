"""HealthMitra Scan – Voice AI Doctor Router"""
import os
import logging
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import VoiceSession
from services.speech_service import transcribe_audio
from services.llm_service import answer_health_question
from config import UPLOAD_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["Voice AI Doctor"])

_pool = ThreadPoolExecutor(max_workers=2)


@router.post("/ask")
async def voice_ask(
    audio: UploadFile = File(None),
    text_query: str = Form(None),
    language: str = Form("en"),
    patient_id: int = Form(None),
    db: Session = Depends(get_db)
):
    """Process voice or text health question and return AI response."""
    try:
        transcript = ""
        loop = asyncio.get_event_loop()

        if audio:
            # Save audio file
            audio_path = os.path.join(UPLOAD_DIR, f"voice_{audio.filename}")
            with open(audio_path, "wb") as f:
                content = await audio.read()
                f.write(content)
            # Speech-to-text (blocking → thread)
            transcript = await loop.run_in_executor(_pool, transcribe_audio, audio_path, language)
        elif text_query:
            transcript = text_query
        else:
            return {"error": "Please provide either audio file or text query"}

        # Get AI response using LLM (blocking → thread)
        ai_response = await loop.run_in_executor(_pool, answer_health_question, transcript, language)

        # Save session
        session = VoiceSession(
            patient_id=patient_id,
            transcript=transcript,
            ai_response=ai_response,
            language=language
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id,
            "transcript": transcript,
            "ai_response": ai_response,
            "language": language
        }

    except Exception as e:
        logger.error(f"Voice ask failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")


@router.post("/text-ask")
async def text_ask(
    question: str = Form(...),
    language: str = Form("en"),
    patient_id: int = Form(None),
    db: Session = Depends(get_db)
):
    """Text-based health Q&A (no audio)."""
    try:
        loop = asyncio.get_event_loop()
        ai_response = await loop.run_in_executor(_pool, answer_health_question, question, language)

        session = VoiceSession(
            patient_id=patient_id,
            transcript=question,
            ai_response=ai_response,
            language=language
        )
        db.add(session)
        db.commit()

        return {
            "question": question,
            "ai_response": ai_response,
            "language": language
        }

    except Exception as e:
        logger.error(f"Text ask failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")


@router.get("/history")
def get_voice_history(patient_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    """Get voice session history."""
    query = db.query(VoiceSession)
    if patient_id:
        query = query.filter(VoiceSession.patient_id == patient_id)
    sessions = query.order_by(VoiceSession.created_at.desc()).limit(limit).all()

    return [{
        "id": s.id,
        "transcript": s.transcript,
        "ai_response": s.ai_response,
        "language": s.language,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in sessions]
