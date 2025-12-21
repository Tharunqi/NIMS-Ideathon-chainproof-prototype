# ChainProof – AI Anomaly Detection Backend

This service simulates or ingests live trades, detects anomalies in real time, and triggers a circuit breaker state.

## Quickstart (Mac/Linux)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000


cat > backend/requirements-dev.txt << 'EOF'
pytest==8.3.3
ruff==0.6.9
httpx==0.27.2
