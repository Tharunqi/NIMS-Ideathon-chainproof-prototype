from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional


BreakerState = Literal["NORMAL", "WATCH", "HALT"]


@dataclass
class Alert:
    ts: float
    symbol: str
    score: float
    reasons: List[str]
    state: BreakerState


class CircuitBreakerPolicy:
    """
    Simple state machine:
    - NORMAL: regular monitoring
    - WATCH: elevated risk
    - HALT: pause trade stream temporarily
    """

    def __init__(self) -> None:
        self.state: BreakerState = "NORMAL"
        self.last_change_ts: float = time.time()
        self.cooldown_until_ts: float = 0.0

        # Keep recent alerts in memory (good enough for hackathon)
        self._alerts: List[Alert] = []
        self._max_alerts = 200

        # thresholds (tuned for your demo)
        self.watch_threshold = 65.0
        self.halt_threshold = 85.0
        self.resume_score_threshold = 35.0

        # timing
        self.halt_seconds = 10.0
        self.watch_grace_seconds = 6.0

        # internal
        self._watch_since: Optional[float] = None

    def reset(self) -> None:
        self.state = "NORMAL"
        self.last_change_ts = time.time()
        self.cooldown_until_ts = 0.0
        self._alerts.clear()
        self._watch_since = None

    def get_state(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "last_change_ts": self.last_change_ts,
            "cooldown_until_ts": self.cooldown_until_ts,
            "watch_since": self._watch_since,
            "thresholds": {
                "watch_threshold": self.watch_threshold,
                "halt_threshold": self.halt_threshold,
                "resume_score_threshold": self.resume_score_threshold,
            },
            "timing": {
                "halt_seconds": self.halt_seconds,
                "watch_grace_seconds": self.watch_grace_seconds,
            },
        }

    def recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [asdict(a) for a in self._alerts[-max(1, min(limit, self._max_alerts)) :]]

    def update(self, symbol: str, score: float, reasons: List[str]) -> Dict[str, Any]:
        now = time.time()
        prev_state = self.state
        event: Optional[Dict[str, Any]] = None

        # If currently halted and cooldown not finished, stay halted
        if self.state == "HALT":
            if now < self.cooldown_until_ts:
                pass
            else:
                # cooldown ended: resume if score is low enough
                if score <= self.resume_score_threshold:
                    self.state = "NORMAL"
                    self.last_change_ts = now
                    self._watch_since = None
                    event = {"type": "breaker", "action": "RESUME", "from": prev_state, "to": self.state}
                else:
                    # extend a bit if still risky
                    self.cooldown_until_ts = now + 3.0

        # NORMAL/WATCH logic
        if self.state != "HALT":
            if score >= self.halt_threshold:
                self.state = "HALT"
                self.last_change_ts = now
                self.cooldown_until_ts = now + self.halt_seconds
                event = {"type": "breaker", "action": "HALT", "from": prev_state, "to": self.state}
            elif score >= self.watch_threshold:
                if self.state == "NORMAL":
                    self.state = "WATCH"
                    self.last_change_ts = now
                    self._watch_since = now
                    event = {"type": "breaker", "action": "WATCH", "from": prev_state, "to": self.state}
                else:
                    # already WATCH; if it persists too long, escalate
                    if self._watch_since and (now - self._watch_since) >= self.watch_grace_seconds:
                        self.state = "HALT"
                        self.last_change_ts = now
                        self.cooldown_until_ts = now + self.halt_seconds
                        event = {"type": "breaker", "action": "HALT", "from": prev_state, "to": self.state}
            else:
                # score low, drop from WATCH to NORMAL
                if self.state == "WATCH":
                    self.state = "NORMAL"
                    self.last_change_ts = now
                    self._watch_since = None
                    event = {"type": "breaker", "action": "NORMALIZE", "from": prev_state, "to": self.state}

        # record alert when score is meaningful
        if score >= self.watch_threshold:
            self._alerts.append(Alert(ts=now, symbol=symbol, score=score, reasons=reasons, state=self.state))
            if len(self._alerts) > self._max_alerts:
                self._alerts = self._alerts[-self._max_alerts :]

        return {
            "state": self.state,
            "event": event,
        }
