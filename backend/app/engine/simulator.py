import asyncio
import random
import time
from dataclasses import dataclass
from typing import Literal

import numpy as np

Scenario = Literal["normal", "attack"]


@dataclass
class TradeEvent:
    ts: float
    symbol: str
    price: float
    qty: int
    side: str


class TradeSimulator:
    def __init__(self) -> None:
        self.scenario: Scenario = "normal"
        self._symbols = ["TCS", "INFY", "HDFCBANK", "RELIANCE", "ICICIBANK"]
        self._base_prices = {s: random.uniform(800, 3500) for s in self._symbols}

    def set_scenario(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def next_trade(self) -> TradeEvent:
        symbol = random.choice(self._symbols)

        drift = np.random.normal(0, 0.6)
        qty = int(max(1, np.random.lognormal(mean=3.0, sigma=0.35)))
        side = "BUY" if random.random() > 0.5 else "SELL"

        if self.scenario == "attack":
            symbol = "RELIANCE"
            drift += np.random.normal(0, 6.0)
            qty = int(max(1, np.random.lognormal(mean=5.0, sigma=0.6)))
            side = "BUY"

        self._base_prices[symbol] = max(1.0, self._base_prices[symbol] + drift)

        return TradeEvent(
            ts=time.time(),
            symbol=symbol,
            price=float(round(self._base_prices[symbol], 2)),
            qty=qty,
            side=side,
        )

    async def run(self, emit_fn, tps: float = 8.0) -> None:
        interval = 1.0 / max(1.0, tps)
        while True:
            trade = self.next_trade()
            await emit_fn(trade)
            await asyncio.sleep(interval)
