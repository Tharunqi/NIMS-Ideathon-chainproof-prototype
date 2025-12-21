from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from app.features.build_features import FeatureBuilder
from app.features.windows import WindowTrade
from app.models.baseline import BaselineAnomalyModel


class ScoringEngine:
    def __init__(self) -> None:
        self._fb = FeatureBuilder()
        self._model = BaselineAnomalyModel()

    def process_trade(self, trade: WindowTrade) -> Dict[str, Any]:
        fv = self._fb.update(trade)
        res = self._model.score(fv)
        return {
            "features": asdict(fv),
            "anomaly": {"score": res.score, "reasons": res.reasons},
        }
