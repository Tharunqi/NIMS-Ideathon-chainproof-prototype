from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from app.features.build_features import FeatureVector


@dataclass
class AnomalyResult:
    score: float  # 0..100
    reasons: List[str]


class BaselineAnomalyModel:
    """
    Baseline hybrid detector:
    - Robust Z scoring on key rolling features
    - Simple rules for judge-friendly reason codes
    """

    def __init__(self) -> None:
        # running history for robust stats (bounded)
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
    def _robust_z(x: float, arr: List[float]) -> float:
        if len(arr) < 30:
            return 0.0
        a = np.array(arr, dtype=float)
        med = float(np.median(a))
        mad = float(np.median(np.abs(a - med))) + 1e-9
        return 0.6745 * (x - med) / mad

    def score(self, fv: FeatureVector) -> AnomalyResult:
        self._push_hist(fv)

        z_tps = self._robust_z(fv.tps_3s, self._hist_tps)
        z_vol = self._robust_z(fv.vol_3s, self._hist_vol)
        z_vel = self._robust_z(fv.price_vel_3s, self._hist_vel)

        reasons: List[str] = []

        # Rule-based reasons (easy to explain on stage)
        if fv.top_symbol_share_3s >= 0.75:
            reasons.append("high_symbol_concentration")
        if fv.large_order_ratio_3s >= 0.35 and fv.avg_qty_3s > 50:
            reasons.append("large_order_burst")
        if z_tps >= 4.0:
            reasons.append("trade_rate_spike")
        if z_vol >= 4.0:
            reasons.append("volume_spike")
        if z_vel >= 4.0:
            reasons.append("price_jump_velocity")

        # score composition
        components: List[Tuple[float, float]] = [
            (abs(z_tps), 20.0),
            (abs(z_vol), 20.0),
            (abs(z_vel), 20.0),
            (fv.top_symbol_share_3s * 40.0, 1.0),
        ]

        raw = 0.0
        for val, w in components:
            raw += min(10.0, val) * w

        # clamp to 0..100
        score = float(max(0.0, min(100.0, raw / 10.0)))

        # If nothing triggered, still provide mild explanation
        if not reasons and score < 20:
            reasons = ["normal_behavior"]

        return AnomalyResult(score=score, reasons=reasons)
