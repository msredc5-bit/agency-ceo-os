"""Layer 0 — shared data models. Plain dataclasses, no dependencies."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Task:
    task_id: str
    business_id: str
    division_id: str
    kind: str               # e.g. "mock_revenue_check", "content_draft"
    payload: dict = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow)


@dataclass
class WorkerResult:
    worker_id: str
    task_id: str
    status: str             # "ok" | "failed" | "skipped"
    output: dict = field(default_factory=dict)
    mock_revenue_usd: float = 0.0   # mock ledger only — never real money
    notes: str = ""
    finished_at: str = field(default_factory=utcnow)


@dataclass
class DivisionReport:
    division_id: str
    division_name: str
    workers_run: int
    workers_ok: int
    mock_revenue_usd: float
    notes: list[str] = field(default_factory=list)


@dataclass
class LedgerEntry:
    entry_id: str
    kind: str               # "mock_revenue" | "mock_cost" | "note"
    amount_usd: float
    business_id: str = ""
    division_id: str = ""
    memo: str = ""
    created_at: str = field(default_factory=utcnow)


@dataclass
class DayReport:
    date: str
    divisions_run: int
    workers_run: int
    workers_ok: int
    mock_revenue_usd: float
    mock_cost_usd: float
    division_reports: list[DivisionReport] = field(default_factory=list)
