# GeoAI — Current Status & Next Steps Plan

> **Last updated:** June 21, 2026 — Session 2 changes applied

## What's Already Built ✅

### Backend (FastAPI)
| Component | Status | Notes |
|---|---|---|
| Auth (register/login/logout/JWT) | ✅ Done | Cookie-based, bcrypt hashed |
| User profiles (GET/PATCH /me) | ✅ Done | |
| Chat sessions (create/list/delete/rename) | ✅ Done | |
| Session history (query logs) | ✅ Done | |
| Session sharing (share tokens) | ✅ Done | |
| Geocoding service | ✅ Real API | Uses Nominatim (OSM) — **free, no key needed** |
| Weather service | ✅ Real API + upgraded | Open-Meteo with humidity, feels-like, UV, precipitation |
| Places/POI service | ✅ Real API + fixed | Overpass OSM with proper User-Agent headers |
| **Ollama LLM integration** | ✅ **NEW — Done** | `qwen2.5-coder:1.5b` via Ollama, tool-calling working |
| **Satellite service** | ✅ **NEW — Done** | NASA GIBS WMTS tiles (free), structured JSON with tile coords |
| Real Estate service | ❌ Fake data | Reads local `sample_listings.json`, needs Kaggle dataset |
| RAG service | ❌ Empty stub | No vector DB connected |
| Database (SQLite → PostgreSQL-ready) | ✅ Done | Alembic migrations in place |
| **Training data generator** | ✅ **NEW — Done** | `generate_training_data.py` — calls real APIs, outputs JSONL |

### Frontend (React + Vite)
| Component | Status | Notes |
|---|---|---|
| Landing page | ✅ Done | |
| Login / Register pages | ✅ Done | |
| Chat page | ✅ Done | |
| Chat history page | ✅ Done | |
| Profile page | ✅ Done | |
| Shared chat page | ✅ Done | |
| Globe visualization | ⚠️ CSS-only | No real 3D globe library wired up |
| Message rendering (Markdown) | ✅ Done | |
| Tool badges | ✅ Done | |

---

## What Remains to Implement

### Phase 1 — Real Data Integration (Short-term, No LLM needed)

These use **already-free APIs** — no cost, no key required for most.

#### 1. Weather — Add humidity & daily forecast (Open-Meteo)
`backend/app/services/weather.py` already calls Open-Meteo but only fetches `current_weather`. The API can also return humidity, precipitation, UV index, 7-day forecast — just add more params.
- **Effort:** 1 hour

#### 2. Real Estate — Real API Integration
Currently reads `sample_listings.json`. Options (free/freemium):
- **MagicBricks / 99acres / Housing.com** — no public API (scraping risky)
- **RapidAPI India Real Estate** — has free tier
- **Best approach for training data:** Build a scraper to collect real listings from public websites and store them in your SQLite DB (`real_estate_listings` table is already created)
- **Effort:** 2–3 days

#### 3. Satellite Imagery — NASA or Mapbox (free tiers)
`backend/app/services/satellite.py` is a stub. Options:
- **NASA GIBS tiles** — completely free, just tile URLs per lat/lon
- **Mapbox Static Images API** — free tier (50K req/month)
- **Sentinel Hub** — free educational tier
- **Effort:** 4–6 hours

#### 4. RAG Service — Connect a vector store
`backend/app/services/rag.py` is empty. For local geospatial knowledge:
- Use **ChromaDB** (local, no server needed) or **pgvector** (if upgrading to Postgres)
- **Effort:** 1–2 days

---

### Phase 2 — Train Your Own LLM (Your Main Goal)

Since you don't want to use a commercial LLM API (GPT/Gemini/Claude), you want to **train your own model**. Here is the full roadmap:

#### Step 1 — Collect Training Data 📊

This is the **most critical step**. Your model needs to learn:
1. How to understand geo-spatial questions
2. When to call which tool (geocoding, weather, places, real estate)
3. How to synthesize tool outputs into natural language

**Data Sources to Collect:**

| Dataset | What it trains | Where to get |
|---|---|---|
| Geo Q&A pairs | Question → Answer about places | MS-MARCO, Natural Questions, TriviaQA |
| Tool-calling examples | Query → `{tool_call, args}` JSON | Synthetic generation (script) |
| Weather Q&A | "What's weather in X?" → structured answer | Generate from Open-Meteo API calls |
| Places Q&A | "Find restaurants near Y" → list | Generate from Overpass API calls |
| Real estate Q&A | "Houses in Z under budget" → listing | Scraped/generated |
| Instruction following | General chat + tool use | Alpaca, FLAN, OpenHermes |

**Estimated data needed:** 10,000–50,000 examples for fine-tuning a small model

#### Step 2 — Choose a Base Model (to fine-tune, NOT train from scratch)

Training from scratch requires millions of GPU hours. Instead, **fine-tune an open-source model**:

| Model | Size | VRAM needed | Notes |
|---|---|---|---|
| **Qwen2.5-1.5B-Instruct** | 1.5B | ~4 GB | Best for low-end GPU, supports tool calling |
| **Phi-3.5-mini-instruct** | 3.8B | ~8 GB | Good reasoning, Microsoft open-source |
| **Llama-3.2-3B-Instruct** | 3B | ~8 GB | Meta open-source, great instruction following |
| **Mistral-7B-Instruct** | 7B | ~16 GB | Best quality if you have GPU |
| **TinyLlama** | 1.1B | ~3 GB | Very small, runs on CPU even |

> [!IMPORTANT]
> **Recommended starting point:** `Qwen2.5-1.5B-Instruct` — it natively supports function/tool calling in its chat template, which is exactly what your agent architecture needs.

#### Step 3 — Fine-tuning Strategy

Use **QLoRA** (Quantized Low-Rank Adaptation) — fine-tunes in 4-bit quantization so it fits on consumer GPUs.

**Tools:**
- `transformers` + `peft` + `trl` (HuggingFace ecosystem)
- `bitsandbytes` for 4-bit quantization
- `datasets` for data loading

**Training format (chat template):**
```json
{
  "messages": [
    {"role": "system", "content": "You are GeoAI-Core, a geospatial assistant..."},
    {"role": "user", "content": "What's the weather in Pune?"},
    {"role": "assistant", "content": "<tool_call>get_weather({\"location\": \"Pune\"})</tool_call>"},
    {"role": "tool", "content": "{\"temperature_celsius\": 32, \"condition\": \"Clear sky\"}"},
    {"role": "assistant", "content": "The current weather in Pune is clear sky with 32°C..."}
  ]
}
```

#### Step 4 — Serving the Model

After fine-tuning, serve via:
- **Ollama** (easiest — just `ollama serve`, drop your GGUF model in)
- **llama.cpp** (CPU inference, very fast for small models)
- **vLLM** (GPU inference server, OpenAI-compatible API)

Your existing `model_loader.py` already has `BaseLLMProvider` abstract class — you just add a new `LocalLLMProvider` class that calls your local server.

---

## Prioritized Action Plan

```
Phase 1 — Real Data (This Week)
  ├── [1] Upgrade weather to fetch humidity + feels_like (1hr)
  ├── [2] Integrate NASA GIBS / Mapbox for satellite thumbnails (4hr)
  └── [3] Build a data scraper for real estate (2–3 days)

Phase 2 — Dataset Collection (Next 2–3 Weeks)
  ├── [4] Write a script to auto-generate tool-call training examples
  │       using your REAL APIs (weather, places, geocoding)
  ├── [5] Download open geo Q&A datasets (MS-MARCO, Natural Questions)
  └── [6] Curate & clean into chat-template JSONL format

Phase 3 — Fine-tune LLM (Week 4–6)
  ├── [7] Set up fine-tuning environment (HuggingFace + QLoRA)
  ├── [8] Fine-tune Qwen2.5-1.5B or Phi-3.5-mini on your dataset
  └── [9] Evaluate with test queries

Phase 4 — Integrate into Backend (Week 6–7)
  ├── [10] Add LocalLLMProvider to model_loader.py
  ├── [11] Serve model via Ollama or vLLM
  └── [12] Replace MockLLMProvider with LocalLLMProvider in config
```

---

## The Immediate Next Step: Data Collection Script

The first real action you should take is **building a script that automatically generates training data** using your own APIs. Here's the approach:

1. Take a list of Indian cities/localities
2. For each: call geocoding → call weather API → call places API
3. Format each interaction as a (query, tool_call, tool_result, final_answer) tuple
4. Save as JSONL — this becomes your training dataset

This gives you **real data from real APIs** to train on — and you can generate thousands of examples automatically.

> [!TIP]
> Want me to build this data collection script as a starting point? It would auto-query your existing services and generate training-ready JSONL files. This is the most impactful next step.

---

## Open Questions

1. **What GPU do you have?** This determines which base model is feasible to fine-tune locally vs. using Google Colab/Kaggle (free GPU).
2. **Satellite imagery** — Do you want static image thumbnails embedded in chat responses, or just metadata (coordinates, date)?
3. **Real estate** — Do you want to scrape real listings from Indian websites, or is synthetic/generated data acceptable for now?
4. **Scope** — Is GeoAI focused on India specifically, or global?
