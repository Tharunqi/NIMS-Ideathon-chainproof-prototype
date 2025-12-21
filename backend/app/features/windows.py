from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable


@dataclass
class WindowTrade:
    ts: float
    symbol: str
    price: float
    qty: int
    side: str


class RollingWindow:
    """
    Keeps trades in a rolling time window (seconds).
    """

    def __init__(self, window_seconds: float) -> None:
        self.window_seconds = float(window_seconds)
        self._buf: Deque[WindowTrade] = deque()

    def push(self, t: WindowTrade) -> None:
        self._buf.append(t)
        self._evict(t.ts)

    def _evict(self, now_ts: float) -> None:
        cutoff = now_ts - self.window_seconds
        while self._buf and self._buf[0].ts < cutoff:
            self._buf.popleft()

    def items(self, now_ts: float) -> Iterable[WindowTrade]:
        self._evict(now_ts)
        return list(self._buf)

    def __len__(self) -> int:
        return len(self._buf)
