from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.engine.simulator import TradeSimulator
from app.engine.stream import ConnectionManager

router = APIRouter(tags=["stream"])

manager = ConnectionManager()
simulator = TradeSimulator()


class ScenarioRequest(BaseModel):
    scenario: str


@router.websocket("/ws/trades")
async def ws_trades(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)


@router.post("/control/scenario")
def set_scenario(payload: ScenarioRequest):
    scenario = payload.scenario.strip().lower()
    if scenario not in ["normal", "attack"]:
        return {"ok": False, "error": "scenario must be 'normal' or 'attack'"}
    simulator.set_scenario(scenario)  # type: ignore[arg-type]
    return {"ok": True, "scenario": simulator.scenario}
