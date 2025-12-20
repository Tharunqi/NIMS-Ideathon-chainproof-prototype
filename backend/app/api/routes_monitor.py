from fastapi import APIRouter

from app.api.routes_stream import policy, last_anomaly

router = APIRouter(tags=["monitor"])


@router.get("/state/breaker")
def get_breaker_state():
    return policy.get_state()


@router.get("/debug/last_anomaly")
def debug_last_anomaly():
    return last_anomaly


@router.get("/alerts/recent")
def get_recent_alerts(limit: int = 50):
    return {"alerts": policy.recent_alerts(limit=limit)}


@router.post("/control/reset")
def reset_policy():
    policy.reset()
    return {"ok": True}
