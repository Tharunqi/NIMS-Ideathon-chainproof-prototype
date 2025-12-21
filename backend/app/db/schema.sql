CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  symbol TEXT NOT NULL,
  price REAL NOT NULL,
  qty INTEGER NOT NULL,
  side TEXT NOT NULL,
  anomaly_score REAL NOT NULL,
  breaker_state TEXT NOT NULL,
  reasons TEXT NOT NULL,
  scenario TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trades_ts ON trades(ts);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);

CREATE TABLE IF NOT EXISTS breaker_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  action TEXT NOT NULL,
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_breaker_events_ts ON breaker_events(ts);
