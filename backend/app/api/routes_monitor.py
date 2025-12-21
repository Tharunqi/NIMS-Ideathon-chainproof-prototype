from fastapi import APIRouter

from app.api.routes_stream import last_anomaly, policy
from app.db.sqlite import AuditDB

router = APIRouter(tags=["monitor"])
db = AuditDB()


@router.get("/state/breaker")
def get_breaker_state():
    return policy.get_state()


@router.get("/debug/last_anomaly")
def debug_last_anomaly():
    return last_anomaly


@router.get("/alerts/recent")
def get_recent_alerts(limit: int = 50):
    return {"alerts": policy.recent_alerts(limit=limit)}


@router.get("/audit/trades")
def audit_trades(limit: int = 50):
    return {"trades": db.recent_trades(limit=limit)}


@router.get("/audit/breaker_events")
def audit_breaker_events(limit: int = 50):
    return {"events": db.recent_breaker_events(limit=limit)}


@router.post("/control/reset")
def reset_policy():
    policy.reset()
    return {"ok": True}
