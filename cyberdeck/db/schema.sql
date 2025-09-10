PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY,
  ts REAL NOT NULL,
  topic TEXT NOT NULL,
  payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY,
  ts REAL NOT NULL,
  kind TEXT NOT NULL,
  title TEXT,
  detail TEXT,
  severity INTEGER DEFAULT 1,
  acknowledged INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS faces (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  embedding BLOB NOT NULL,
  added_ts REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs(ts);
CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts(ts);
