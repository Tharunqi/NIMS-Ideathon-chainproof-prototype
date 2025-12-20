from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from app.features.windows import RollingWindow, WindowTrade


@dataclass
class FeatureVector:
    ts: float
    symbol: str
    tps_3s: float
    vol_3s: float
    avg_qty_3s: float
    price_vel_3s: float
    top_symbol_share_3s: float
    large_order_ratio_3s: float


class FeatureBuilder:
    """
    Builds rolling-window features per incoming trade.
    """

    def __init__(self) -> None:
        self.w3 = RollingWindow(3.0)
        self._last_price: Dict[str, float] = {}

    def update(self, trade: WindowTrade) -> FeatureVector:
        self.w3.push(trade)
        items: List[WindowTrade] = list(self.w3.items(trade.ts))

        tps = len(items) / 3.0
        vol = float(sum(x.qty for x in items)) / 3.0
        avg_qty = float(np.mean([x.qty for x in items])) if items else 0.0

        # price velocity: mean absolute delta per second for the trade's symbol
        deltas = []
        prev = None
        for x in items:
            if x.symbol != trade.symbol:
                continue
            if prev is not None:
                deltas.append(abs(x.price - prev))
            prev = x.price
        price_vel = (float(np.mean(deltas)) / 3.0) if deltas else 0.0

        # symbol concentration
        sym_counts = Counter([x.symbol for x in items])
        top_share = 0.0
        if sym_counts:
            top_share = max(sym_counts.values()) / max(1, len(items))

        # large order ratio: share of trades in window with qty above 90th percentile
        qtys = [x.qty for x in items] or [1]
        p90 = float(np.percentile(qtys, 90))
        large_ratio = float(sum(1 for q in qtys if q >= p90)) / max(1, len(qtys))

        self._last_price[trade.symbol] = trade.price

        return FeatureVector(
            ts=trade.ts,
            symbol=trade.symbol,
            tps_3s=float(tps),
            vol_3s=float(vol),
            avg_qty_3s=float(avg_qty),
            price_vel_3s=float(price_vel),
            top_symbol_share_3s=float(top_share),
            large_order_ratio_3s=float(large_ratio),
        )
