from fastapi import APIRouter
from pydantic import BaseModel

from app.api.routes_stream import policy

router = APIRouter(tags=["monitor"])


class ResetResponse(BaseModel):
    ok: bool


@router.get("/state/breaker")
def get_breaker_state():
    return policy.get_state()


@router.get("/alerts/recent")
def get_recent_alerts(limit: int = 50):
    return {"alerts": policy.recent_alerts(limit=limit)}


@router.post("/control/reset")
def reset_policy():
    policy.reset()
    return {"ok": True}
