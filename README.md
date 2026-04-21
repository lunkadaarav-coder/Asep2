## HealthMitra Scan Project Summary

### Purpose & Target Users
HealthMitra Scan is an **offline multilingual AI-powered health assistant** designed for rural India. It enables users to analyze medical reports, scan food for nutritional insights, consult an AI doctor via voice/text, predict health risks, and maintain personal health records - all without internet connectivity. Primary users include rural patients, ASHA workers, and individuals with limited healthcare access.

### Architecture
- **Backend**: FastAPI (Python) with SQLite database, SQLAlchemy ORM, JWT authentication, and local file storage
- **Frontend**: React 18 with Vite, React Router, and custom CSS styling
- **Database**: 6 models (Users, Patients, MedicalReports, FoodScans, HealthTimeline, VoiceSessions)

### Key Features
- **Medical Report Explainer**: PDF/image upload → OCR → AI analysis → bilingual explanations → risk scoring
- **Food Scanner**: Camera-based Indian food detection → nutrition analysis → health warnings  
- **Meal Scanner**: Multi-food plate analysis → safety classification → health scores
- **Voice AI Doctor**: Voice/text Q&A → real LLM responses → English/Hindi support
- **Risk Predictor**: Vitals input → diabetes/heart risk calculation → personalized recommendations
- **Health Memory**: Local storage → filterable timeline → complete health history
- **AI Health Twin**: Digital profile → vital monitoring → AI insights
- **Rural ASHA Mode**: Multi-patient registry → village-wise management
- **Offline AI Mode**: CPU/NPU monitoring → 100% offline operation

### Main Components
- **Backend Services** (8): LLM (Ollama), Clinical Engine, Risk Engine, Food Detector (YOLOv8), Meal Classifier (EfficientNet), OCR (Tesseract), Speech (Whisper), Alert Service
- **Backend Routers** (10): Auth, Reports, Food, Voice, Risk, Patients, System, Dashboard, Health Twin, Meal
- **Frontend Pages** (13): Dashboard, Report Explainer, Food Scanner, Meal Scanner, Voice Doctor, Risk Predictor, Health Memory, Health Twin, Rural Mode, Offline Mode, Login, Signup, Profile

### Current Status
**Working Prototype (v2.0.0)** - Core functionality implemented, offline-first architecture, bilingual support, real AI integrations with comprehensive fallbacks. Demo-ready with simulated responses when AI models unavailable.

### Notable Technologies
- **AI/ML**: Ollama (local LLMs), YOLOv8, EfficientNet-B4, Whisper, Tesseract
- **Offline-First**: SQLite, local storage, AMD Ryzen AI optimization
- **Multilingual**: English/Hindi processing with localized health terminology
- **Indian Focus**: Comprehensive food nutrition database, local medical guidelines, ASHA worker features

### Project Structure
```
healthmitra-scan/
├── backend/          # FastAPI app (main.py, routers/, services/)
├── frontend/         # React SPA (App.jsx, pages/)
├── requirements.txt  # Python deps
└── README.md         # Documentation
```

This is a well-architected health assistant bridging advanced AI with rural healthcare accessibility, featuring robust offline functionality and comprehensive fallback systems.
