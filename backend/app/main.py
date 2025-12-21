import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_monitor import router as monitor_router
from app.api.routes_stream import enrich_trade, manager, simulator
from app.api.routes_stream import router as stream_router
from app.core.config import settings
from app.db.sqlite import AuditDB

db = AuditDB()

app = FastAPI(title="ChainProof AI Shield", version="0.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(stream_router)
app.include_router(monitor_router)


@app.on_event("startup")
async def startup():
    db.init_schema()

    async def emit(trade):
        payload = enrich_trade(trade)

        reasons_str = ",".join(payload["anomaly"]["reasons"])
        db.insert_trade(
            {
                "ts": payload["ts"],
                "symbol": payload["symbol"],
                "price": payload["price"],
                "qty": payload["qty"],
                "side": payload["side"],
                "anomaly_score": payload["anomaly"]["score"],
                "breaker_state": payload["breaker"]["state"],
                "reasons": reasons_str,
                "scenario": payload["anomaly"]["reasons"][0]
                if payload["anomaly"]["reasons"]
                else "unknown",
            }
        )

        if payload.get("breaker_event"):
            ev = payload["breaker_event"]
            db.insert_breaker_event(ev["action"], ev["from"], ev["to"])

        await manager.broadcast({"type": "trade", "data": payload})

        if payload.get("breaker_event"):
            await manager.broadcast({"type": "breaker", "data": payload["breaker_event"]})

    asyncio.create_task(simulator.run(emit_fn=emit, tps=10.0))
