"""Layer 0 — Store interface. SQLite today, Postgres tomorrow (same interface)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import DayReport, LedgerEntry, Task, WorkerResult


class Store(ABC):
    @abstractmethod
    def init(self) -> None: ...

    @abstractmethod
    def save_task(self, task: Task) -> None: ...

    @abstractmethod
    def save_result(self, result: WorkerResult) -> None: ...

    @abstractmethod
    def save_ledger(self, entry: LedgerEntry) -> None: ...

    @abstractmethod
    def save_day_report(self, report: DayReport) -> None: ...

    @abstractmethod
    def totals(self) -> dict:
        """Return {'mock_revenue_usd': x, 'mock_cost_usd': y, 'tasks': n, ...}."""
