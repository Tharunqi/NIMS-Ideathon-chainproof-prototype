from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.engine.policy import CircuitBreakerPolicy
from app.engine.scorer import ScoringEngine
from app.engine.simulator import TradeSimulator
from app.engine.stream import ConnectionManager
from app.features.windows import WindowTrade

router = APIRouter(tags=["stream"])

manager = ConnectionManager()
simulator = TradeSimulator()
scorer = ScoringEngine()
policy = CircuitBreakerPolicy()


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


def enrich_trade(trade) -> dict:
    wt = WindowTrade(
        ts=trade.ts,
        symbol=trade.symbol,
        price=trade.price,
        qty=trade.qty,
        side=trade.side,
    )
    scored = scorer.process_trade(wt)

    score = float(scored["anomaly"]["score"])
    reasons = list(scored["anomaly"]["reasons"])

    pol = policy.update(symbol=wt.symbol, score=score, reasons=reasons)

    # Pause trade stream if HALT
    simulator.set_paused(pol["state"] == "HALT")

    return {
        "ts": wt.ts,
        "symbol": wt.symbol,
        "price": wt.price,
        "qty": wt.qty,
        "side": wt.side,
        "anomaly": scored["anomaly"],
        "features": scored["features"],
        "breaker": {"state": pol["state"]},
        "breaker_event": pol["event"],
    }
