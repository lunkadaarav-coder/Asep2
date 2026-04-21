# 🏥 HealthMitra Scan

An **offline multilingual AI-powered health assistant** designed to make healthcare accessible in low-resource and rural environments.

---

## 🎯 Purpose

HealthMitra Scan enables users to:
- Analyze medical reports  
- Scan food for nutritional insights  
- Consult an AI doctor (voice/text)  
- Predict health risks  
- Maintain complete health records  

All while operating **100% offline**.

---

## 👥 Target Users

- Rural patients  
- ASHA workers  
- Individuals with limited healthcare access  

---

## 🏗️ System Architecture

### 🔹 Backend
- FastAPI (Python)
- SQLite Database
- SQLAlchemy ORM
- JWT Authentication
- Local file storage

### 🔹 Frontend
- React 18 (Vite)
- React Router
- Custom CSS UI

### 🔹 Database Models
- Users  
- Patients  
- MedicalReports  
- FoodScans  
- HealthTimeline  
- VoiceSessions  

---

## 🚀 Key Features

### 📄 Medical Report Explainer
- PDF/Image → OCR → AI analysis → bilingual explanation → risk scoring  

### 📸 Food Scanner
- Indian food detection → nutrition analysis → health warnings  

### 🍽️ Meal Scanner
- Multi-food detection → safety classification → health scoring  

### 🎤 Voice AI Doctor
- Voice/Text queries → real LLM responses → Hindi + English  

### 📊 Risk Predictor
- Vitals input → diabetes & heart risk prediction → recommendations  

### 📅 Health Memory
- Local storage → filterable timeline → complete history  

### 👤 AI Health Twin
- Digital health profile → trends → AI insights  

### 🏥 Rural ASHA Mode
- Multi-patient registry → village-level management  

### 💻 Offline AI Mode
- CPU/NPU monitoring → full offline AI execution  

---

## 🧠 Core AI Components

### Backend Services (8)
- LLM (Ollama)
- Clinical Engine
- Risk Engine
- Food Detector (YOLOv8)
- Meal Classifier (EfficientNet-B4)
- OCR Engine (Tesseract)
- Speech Engine (Whisper)
- Alert Service

---

## 🔌 API Architecture

### Backend Routers (10)
- Auth  
- Reports  
- Food  
- Voice  
- Risk  
- Patients  
- System  
- Dashboard  
- Health Twin  
- Meal  

---

## 🖥️ Frontend Modules

### Pages (13)
- Dashboard  
- Report Explainer  
- Food Scanner  
- Meal Scanner  
- Voice Doctor  
- Risk Predictor  
- Health Memory  
- Health Twin  
- Rural Mode  
- Offline Mode  
- Login  
- Signup  
- Profile  

---

## ⚙️ Tech Stack

### 🧠 AI / ML
- Ollama (Local LLMs)
- YOLOv8
- EfficientNet-B4
- Whisper
- Tesseract OCR

### 🧱 Core Stack
- Python (FastAPI)
- React (Vite)
- SQLite
- SQLAlchemy

### 🌍 System Design
- Offline-first architecture  
- Local data storage (privacy-first)  
- AMD Ryzen AI optimization  

---

## 📌 Current Status

✅ **Working Prototype (v2.0.0)**  
- Fully functional core modules  
- Bilingual support (English + Hindi)  
- Offline AI integration with fallback mechanisms  
- Demo-ready  

---

## 🔒 Key Highlights

- 100% Offline Operation  
- Privacy-first (no cloud dependency)  
- Designed for rural healthcare use cases  
- Supports multilingual interaction  
- Robust fallback system when AI models are unavailable  

---

## 📂 Project Structure

```bash
healthmitra-scan/
├── backend/          # FastAPI app (main.py, routers/, services/)
├── frontend/         # React SPA (App.jsx, pages/)
├── requirements.txt
└── README.md
```

---

## 🧪 Note

This project uses **synthetic and test data** for demonstration and evaluation purposes.

---

## 👨‍💻 Authors

Aarav & Team
