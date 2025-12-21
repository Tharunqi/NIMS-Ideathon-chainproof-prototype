from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from app.features.build_features import FeatureVector


@dataclass
class AnomalyResult:
    score: float  # 0..100
    reasons: List[str]


class BaselineAnomalyModel:
    """
    Judge-friendly detector:
    - Produces a stable 0..100 score
    - Emits reason codes (explainability)
    - Works even with little history (important for live demo)
    """

    def __init__(self) -> None:
        self._hist_tps: List[float] = []
        self._hist_vol: List[float] = []
        self._hist_vel: List[float] = []
        self._max_hist = 2000

    def _push_hist(self, fv: FeatureVector) -> None:
        self._hist_tps.append(fv.tps_3s)
        self._hist_vol.append(fv.vol_3s)
        self._hist_vel.append(fv.price_vel_3s)

        if len(self._hist_tps) > self._max_hist:
            self._hist_tps = self._hist_tps[-self._max_hist :]
            self._hist_vol = self._hist_vol[-self._max_hist :]
            self._hist_vel = self._hist_vel[-self._max_hist :]

    @staticmethod
    def _z(x: float, arr: List[float]) -> float:
        # Works even with small history: use mean/std early, robust MAD later.
        if len(arr) < 10:
            return 0.0
        a = np.array(arr, dtype=float)
        if len(arr) < 30:
            mu = float(np.mean(a))
            sd = float(np.std(a)) + 1e-9
            return (x - mu) / sd
        med = float(np.median(a))
        mad = float(np.median(np.abs(a - med))) + 1e-9
        return 0.6745 * (x - med) / mad

    @staticmethod
    def _clip01(x: float) -> float:
        return float(max(0.0, min(1.0, x)))

    def score(self, fv: FeatureVector) -> AnomalyResult:
        self._push_hist(fv)

        z_tps = abs(self._z(fv.tps_3s, self._hist_tps))
        z_vol = abs(self._z(fv.vol_3s, self._hist_vol))
        z_vel = abs(self._z(fv.price_vel_3s, self._hist_vel))

        reasons: List[str] = []

        # Explainability rules
        if fv.top_symbol_share_3s >= 0.65:
            reasons.append("high_symbol_concentration")
        if fv.large_order_ratio_3s >= 0.30 and fv.avg_qty_3s >= 60:
            reasons.append("large_order_burst")
        if z_tps >= 3.5:
            reasons.append("trade_rate_spike")
        if z_vol >= 3.5:
            reasons.append("volume_spike")
        if z_vel >= 3.5:
            reasons.append("price_jump_velocity")

        # Map to 0..100 using multiple signals
        s_tps = self._clip01(z_tps / 6.0)
        s_vol = self._clip01(z_vol / 6.0)
        s_vel = self._clip01(z_vel / 6.0)

        s_conc = self._clip01((fv.top_symbol_share_3s - 0.30) / 0.70)
        s_large = self._clip01((fv.large_order_ratio_3s - 0.20) / 0.80)
        s_qty = self._clip01((fv.avg_qty_3s - 30.0) / 200.0)

        score = 100.0 * (
            0.25 * s_tps
            + 0.25 * s_vol
            + 0.20 * s_vel
            + 0.15 * s_conc
            + 0.10 * s_large
            + 0.05 * s_qty
        )

        # Deterministic demo boosts (so attack triggers breaker fast)
        if "high_symbol_concentration" in reasons:
            score = max(score, 75.0)
        if "large_order_burst" in reasons:
            score = max(score, 82.0)
        if "price_jump_velocity" in reasons:
            score = max(score, 88.0)
        if "trade_rate_spike" in reasons or "volume_spike" in reasons:
            score = max(score, 80.0)

        if not reasons and score < 20:
            reasons = ["normal_behavior"]

        return AnomalyResult(score=float(min(100.0, max(0.0, score))), reasons=reasons)
