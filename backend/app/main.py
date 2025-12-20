import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_monitor import router as monitor_router
from app.api.routes_stream import router as stream_router, manager, simulator, enrich_trade
from app.core.config import settings

app = FastAPI(title="ChainProof AI Shield", version="0.4.0")

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
    async def emit(trade):
        payload = enrich_trade(trade)
        await manager.broadcast({"type": "trade", "data": payload})

        # if breaker event happened, broadcast it too
        if payload.get("breaker_event"):
            await manager.broadcast({"type": "breaker", "data": payload["breaker_event"]})

    asyncio.create_task(simulator.run(emit_fn=emit, tps=10.0))
