"""Store — SQLite implementation of contracts/store.py."""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict
from pathlib import Path

from src.contracts.models import DayReport, LedgerEntry, Task, WorkerResult
from src.contracts.store import Store

SCHEMA = Path(__file__).with_name("schema.sql").read_text()


class SQLiteStore(Store):
    def __init__(self, path: str = "data/conglomerate.db"):
        self.path = path

    def _conn(self) -> sqlite3.Connection:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self._conn() as c:
            c.executescript(SCHEMA)

    def save_task(self, task: Task) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO tasks VALUES (?,?,?,?,?,?)",
                (task.task_id, task.business_id, task.division_id,
                 task.kind, json.dumps(task.payload), task.created_at),
            )

    def save_result(self, result: WorkerResult) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO results VALUES (?,?,?,?,?,?,?)",
                (result.task_id, result.worker_id, result.status,
                 json.dumps(result.output), result.mock_revenue_usd,
                 result.notes, result.finished_at),
            )

    def save_ledger(self, entry: LedgerEntry) -> None:
        if not entry.entry_id:
            entry.entry_id = uuid.uuid4().hex[:12]
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO ledger VALUES (?,?,?,?,?,?,?)",
                (entry.entry_id, entry.kind, entry.amount_usd,
                 entry.business_id, entry.division_id, entry.memo,
                 entry.created_at),
            )

    def save_day_report(self, report: DayReport) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO day_reports VALUES (?,?,?,?,?,?,?)",
                (report.date, report.divisions_run, report.workers_run,
                 report.workers_ok, report.mock_revenue_usd,
                 report.mock_cost_usd, json.dumps(asdict(report))),
            )

    def totals(self) -> dict:
        with self._conn() as c:
            rev = c.execute(
                "SELECT COALESCE(SUM(amount_usd),0) FROM ledger WHERE kind='mock_revenue'"
            ).fetchone()[0]
            cost = c.execute(
                "SELECT COALESCE(SUM(amount_usd),0) FROM ledger WHERE kind='mock_cost'"
            ).fetchone()[0]
            tasks = c.execute("SELECT COUNT(*) FROM results").fetchone()[0]
            ok = c.execute("SELECT COUNT(*) FROM results WHERE status='ok'").fetchone()[0]
        return {
            "mock_revenue_usd": round(rev, 2),
            "mock_cost_usd": round(cost, 2),
            "tasks": tasks,
            "tasks_ok": ok,
        }

    # -- batch fast paths (single transaction; used by the CEO at scale) ----
    def save_tasks_batch(self, tasks: list[Task]) -> None:
        with self._conn() as c:
            c.executemany(
                "INSERT OR REPLACE INTO tasks VALUES (?,?,?,?,?,?)",
                [(t.task_id, t.business_id, t.division_id, t.kind,
                  json.dumps(t.payload), t.created_at) for t in tasks],
            )

    def save_results_batch(self, results: list[WorkerResult]) -> None:
        with self._conn() as c:
            c.executemany(
                "INSERT OR REPLACE INTO results VALUES (?,?,?,?,?,?,?)",
                [(r.task_id, r.worker_id, r.status, json.dumps(r.output),
                  r.mock_revenue_usd, r.notes, r.finished_at) for r in results],
            )
