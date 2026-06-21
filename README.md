<div align="center">
  <h1>🌍 Geo-Scout AI</h1>
  <p><strong>An Intelligent Full-Stack Agent for Geographical Queries & Real Estate</strong></p>

  <!-- Badges -->
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E" />
  <img src="https://img.shields.io/badge/Ollama-black?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</div>

## 📌 Overview

Geo-Scout AI is a completely local, privacy-first, full-stack AI agent capable of answering complex geographical queries, retrieving live weather data, searching for local amenities, and querying real estate listings. It leverages a custom fine-tuned Large Language Model (`qwen2.5-coder-1.5b`) running locally via **Ollama**, making it fast, free, and entirely offline.

## ✨ Key Features

- **🧠 Local LLM Orchestration:** Powered by a custom fine-tuned `qwen2.5-coder` model running locally. The model intelligently parses user intents, extracts arguments, and dynamically executes backend tools.
- **🏠 Real Estate Search:** Query a local SQLite database for property listings (populated using Kaggle datasets).
- **⛅ Live Weather Data:** Fetches real-time weather information for any coordinates using the Open-Meteo API.
- **📍 Geocoding & Amenities:** Automatically converts plain text locations to Lat/Long using Nominatim, and queries nearby places via Overpass API.
- **🎨 Beautiful React UI:** A sleek, dark-mode focused frontend built with React and Vite. Features real-time typing indicators and visual tool-call badges.
- **🐳 CI/CD & Docker Ready:** Comes with a `docker-compose.yml` for 1-click deployments of the entire stack (Backend, Frontend, and Ollama server), plus GitHub Actions for automated testing.

## 📁 Repository Structure

GeoAI follows a modular Monorepo structure, strictly separating the application layer from the machine learning pipeline:

```text
GeoAI/
├── .github/workflows/   # CI/CD pipelines
├── backend/             # FastAPI App, SQLAlchemy, API Routers, Tool Integrations
├── frontend/            # React + Vite application
├── mlops/               # Fine-tuning scripts, Jupyter Notebooks, raw datasets, GGUF models
├── scripts/             # Data loading & DB initialization utilities
├── docs/                # Architecture diagrams and setup guides
└── docker-compose.yml   # Local environment orchestration
```

## 🛠️ Technology Stack

| Category | Technologies Used |
|---|---|
| **Frontend** | React, Vite, Custom CSS, Fetch API |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic, HTTPX |
| **Database** | SQLite, aiosqlite, SQLAlchemy, Alembic |
| **ML & AI** | Ollama, Unsloth, HuggingFace TRL, Qwen2.5-Coder |
| **DevOps** | Docker, Docker Compose, GitHub Actions |

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
- [Node.js (v20+)](https://nodejs.org/)
- [Python 3.11+](https://www.python.org/)
- [Ollama](https://ollama.com/) (For local AI generation)

### 2. Setup the LLM
Download your fine-tuned `.gguf` file into `mlops/models/` and build it with Ollama:
```bash
cd mlops/models
ollama create geoai_custom -f Modelfile
```

### 3. Start the Backend
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Or .venv/bin/activate on Mac/Linux
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload
```

### 4. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

*(Alternatively, use `docker-compose up -d --build` to launch the entire stack automatically!)*

## 📚 Documentation
For more detailed information about the architecture and database setup, check the `docs/` directory:
- [Architecture Guide](docs/architecture.txt)
- [Database Setup](docs/README_DB.md)

---
<div align="center">
  <i>Built as an experiment in completely local, privacy-first AI workflows.</i>
</div>
