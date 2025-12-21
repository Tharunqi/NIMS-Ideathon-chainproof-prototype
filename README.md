# ChainProof AI Shield (Prototype)

Backend service for a circuit-breaker style market surveillance demo:
- Streams simulated trades
- Computes anomaly score with rule-based signals
- Triggers WATCH/HALT breaker states based on thresholds
- Logs audit events to SQLite
- Exposes OpenAPI docs via FastAPI

## Tech
- FastAPI + Uvicorn
- Ruff (lint/format)
- Pytest
- SQLite audit log

## Quickstart (Backend)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000


