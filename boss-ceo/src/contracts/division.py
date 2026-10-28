"""Layer 0 — DivisionManager interface. One manager == one division (40 businesses)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import DivisionReport, Task
from .worker import Worker


class DivisionManager(ABC):
    division_id: str
    division_name: str

    @abstractmethod
    def register_worker(self, worker: Worker) -> None: ...

    @abstractmethod
    def dispatch(self, tasks: list[Task]) -> DivisionReport:
        """Run tasks across this division's workers, return the rollup."""

    @abstractmethod
    def worker_count(self) -> int: ...
