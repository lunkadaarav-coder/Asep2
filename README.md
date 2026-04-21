# 🏥 HealthMitra Scan

> A offline multilingual AI health assistant powered by AMD Ryzen AI

![Status](https://img.shields.io/badge/Status-Working_Prototype-brightgreen)
![AI](https://img.shields.io/badge/AI-Ollama_LLM-blue)
![Platform](https://img.shields.io/badge/Platform-AMD_Ryzen_AI-orange)
![Offline](https://img.shields.io/badge/Mode-100%25_Offline-green)

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📄 **Medical Report Explainer** | Upload PDF/image → OCR → AI explanation in Hindi & English → Risk Score |
| 📸 **Food Scanner** | Camera-based Indian food detection → Nutrition analysis → Health warnings |
| 🍽️ **Meal Scanner** | Multi-food plate detection → Safe/Unsafe classification → Meal health score |
| 🎤 **Voice AI Doctor** | Voice/text health Q&A → Real LLM response → Bilingual support |
| 📊 **Future Risk Predictor** | Vitals input → Diabetes & Heart risk prediction → Animated gauges |
| 🚨 **Emergency Alert** | Auto-detect critical values → Pulsing red alerts → Bilingual warnings |
| 📅 **Health Memory** | Local storage → Filterable timeline → Complete health history |
| 👤 **AI Health Twin** | Digital profile → Vital monitoring → AI insights with sparklines |
| 🏥 **Rural ASHA Mode** | Multi-patient registry → Village-wise management → Report scanning |
| 💻 **AMD Offline AI Mode** | CPU/NPU/RAM gauges → Model status → 100% offline operation |

## 🛠️ Tech Stack

- **Frontend**: React 18 + Vite + Lucide Icons
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **AI/LLM**: Ollama (Phi-3 / Llama 3) – Real local LLM
- **OCR**: Tesseract (simulated for demo)
- **Food Detection**: YOLOv8 (simulated for demo)
- **Speech**: Whisper (simulated for demo)
- **Database**: SQLite (fully offline)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) [Ollama](https://ollama.ai/) for real LLM responses

### Setup
```bash
# 1. Install backend dependencies
cd healthmitra-scan
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend
npm install

# 3. (Optional) Install Ollama and pull a model
# Download from https://ollama.ai/
ollama pull phi3
```

### Run
```bash
# Terminal 1: Start backend
cd healthmitra-scan/backend
python main.py
# → API docs at http://localhost:8000/docs

# Terminal 2: Start frontend
cd healthmitra-scan/frontend
npm run dev
# → Open http://localhost:5173
```

## 📂 Project Structure

```
healthmitra-scan/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Configuration
│   ├── database.py           # SQLite + SQLAlchemy
│   ├── models.py             # Database models
│   ├── schemas.py            # API schemas
│   ├── routers/              # 6 API route modules
│   └── services/             # 6 AI service modules
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # App shell + routing
│   │   ├── index.css         # Design system
│   │   └── pages/            # 10 feature pages
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── setup.bat
└── README.md
```

## 🎬 Demo Script

1. **Dashboard** → Show overview, stats, quick actions
2. **Report Explainer** → Upload any PDF → Show OCR + bilingual AI explanation + risk gauge
3. **Food Scanner** → Upload food photo → Show detected items + nutrition + warnings
4. **Voice Doctor** → Type/speak health question → Show real LLM response
5. **Risk Predictor** → Enter sample vitals → Show animated diabetes & heart risk gauges
6. **Health Memory** → Show timeline of all past scans/reports
7. **Health Twin** → Show digital profile with vital trends + AI insights
8. **Rural Mode** → Add patient → Show multi-patient management
9. **Offline Mode** → Show live CPU/NPU gauges → All models running locally

## 🏆  Highlights

- ✅ **100% Offline** – No internet required
- ✅ **Real LLM** – Ollama integration for genuine AI responses
- ✅ **Bilingual** – Hindi + English support
- ✅ **AMD Optimized** – Designed for Ryzen AI NPU
- ✅ **Privacy First** – All data stays on device
- ✅ **Rural Ready** – ASHA worker multi-patient support

## 📜 License

MIT License – Built for amd  2025
