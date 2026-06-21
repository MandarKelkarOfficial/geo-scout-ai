# Setup & Execution Guide

This guide explains how to set up the environment, run the GeoAI FastAPI server, and execute the automated test suite.

## Prerequisites
- Python 3.11 or newer

## 1. Environment Setup

First, create a virtual environment and install the required dependencies.

### Windows (PowerShell)
```powershell
# Create a virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Running the Server

Once dependencies are installed, you can start the FastAPI development server using `uvicorn`. Ensure you are running this from the `backend` directory.

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 1001 --reload
```

**Expected Outcome:**
You should see output similar to:
```
INFO:     Uvicorn running on http://0.0.0.0:1001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
You can now visit the API documentation (Swagger UI) in your browser at:
`http://localhost:1001/docs`

## 3. Running the Automated Tests

The application has a comprehensive test suite built with `pytest` and `respx` for mocking external network calls.

Ensure your virtual environment is active, set the `PYTHONPATH`, and run `pytest`.

### Windows (PowerShell)
```powershell
$env:PYTHONPATH="."
python -m pytest tests/
```

### macOS/Linux
```bash
PYTHONPATH="." python -m pytest tests/
```

**Expected Outcome:**
You should see `pytest` discover and run 29 items (tests). It will output a success summary without errors:

```
============================= test session starts =============================
platform win32 -- Python 3.13.x, pytest-x.x.x, pluggy-x.x.x
rootdir: C:\...\GeoAI\backend
plugins: anyio, asyncio, respx
collected 29 items

tests\api\v1\routes\test_health.py ..                                    [  6%]
...
tests\services\test_weather.py ..                                        [100%]

============================= 29 passed in X.XXs ==============================
```
