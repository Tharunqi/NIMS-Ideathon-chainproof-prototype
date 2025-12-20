from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = os.environ.get("CHAINPROOF_DB_PATH", "chainproof_audit.db")


class AuditDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        if self._conn is not None:
            return
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")

    def init_schema(self) -> None:
        self.connect()
        assert self._conn is not None
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        self._conn.executescript(schema)
        self._conn.commit()

    def insert_trade(self, row: Dict[str, Any]) -> None:
        self.connect()
        assert self._conn is not None
        self._conn.execute(
            """
            INSERT INTO trades (ts, symbol, price, qty, side, anomaly_score, breaker_state, reasons, scenario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                float(row["ts"]),
                str(row["symbol"]),
                float(row["price"]),
                int(row["qty"]),
                str(row["side"]),
                float(row["anomaly_score"]),
                str(row["breaker_state"]),
                str(row["reasons"]),
                str(row["scenario"]),
            ),
        )
        self._conn.commit()

    def insert_breaker_event(self, action: str, from_state: str, to_state: str) -> None:
        self.connect()
        assert self._conn is not None
        now = time.time()
        self._conn.execute(
            """
            INSERT INTO breaker_events (ts, action, from_state, to_state)
            VALUES (?, ?, ?, ?)
            """,
            (float(now), str(action), str(from_state), str(to_state)),
        )
        self._conn.commit()

    def recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        self.connect()
        assert self._conn is not None
        cur = self._conn.execute(
            """
            SELECT ts, symbol, price, qty, side, anomaly_score, breaker_state, reasons, scenario
            FROM trades ORDER BY ts DESC LIMIT ?
            """,
            (int(limit),),
        )
        rows = cur.fetchall()
        return [
            {
                "ts": r[0],
                "symbol": r[1],
                "price": r[2],
                "qty": r[3],
                "side": r[4],
                "anomaly_score": r[5],
                "breaker_state": r[6],
                "reasons": r[7],
                "scenario": r[8],
            }
            for r in rows
        ]

    def recent_breaker_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        self.connect()
        assert self._conn is not None
        cur = self._conn.execute(
            """
            SELECT ts, action, from_state, to_state
            FROM breaker_events ORDER BY ts DESC LIMIT ?
            """,
            (int(limit),),
        )
        rows = cur.fetchall()
        return [
            {"ts": r[0], "action": r[1], "from_state": r[2], "to_state": r[3]}
            for r in rows
        ]
