-- AI Conglomerate — local shell schema (SQLite).
-- Portable to Postgres: same tables, same columns (TIMESTAMPTZ -> TEXT here).

CREATE TABLE IF NOT EXISTS tasks (
    task_id     TEXT PRIMARY KEY,
    business_id TEXT NOT NULL,
    division_id TEXT NOT NULL,
    kind        TEXT NOT NULL,
    payload     TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    task_id          TEXT PRIMARY KEY,
    worker_id        TEXT NOT NULL,
    status           TEXT NOT NULL,
    output           TEXT NOT NULL DEFAULT '{}',
    mock_revenue_usd REAL NOT NULL DEFAULT 0,
    notes            TEXT NOT NULL DEFAULT '',
    finished_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger (
    entry_id    TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,              -- mock_revenue | mock_cost | note
    amount_usd  REAL NOT NULL DEFAULT 0,
    business_id TEXT NOT NULL DEFAULT '',
    division_id TEXT NOT NULL DEFAULT '',
    memo        TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS day_reports (
    date             TEXT PRIMARY KEY,
    divisions_run    INTEGER NOT NULL,
    workers_run      INTEGER NOT NULL,
    workers_ok       INTEGER NOT NULL,
    mock_revenue_usd REAL NOT NULL,
    mock_cost_usd    REAL NOT NULL,
    report           TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_results_worker ON results(worker_id);
CREATE INDEX IF NOT EXISTS idx_tasks_division ON tasks(division_id);
CREATE INDEX IF NOT EXISTS idx_ledger_division ON ledger(division_id);
