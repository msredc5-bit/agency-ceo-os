"""Layer 3 — DivisionManager template: runs its workers, rolls up the report."""
from __future__ import annotations

from src.contracts.division import DivisionManager
from src.contracts.models import DivisionReport, Task
from src.contracts.worker import Worker


class DivisionManagerBase(DivisionManager):
    def __init__(self, division_id: str, division_name: str):
        self.division_id = division_id
        self.division_name = division_name
        self._workers: list[Worker] = []
        self.last_results: list = []  # WorkerResult list from the latest dispatch

    def register_worker(self, worker: Worker) -> None:
        self._workers.append(worker)

    @property
    def workers(self) -> list[Worker]:
        return list(self._workers)

    def worker_count(self) -> int:
        return len(self._workers)

    def dispatch(self, tasks: list[Task]) -> DivisionReport:
        mine = [t for t in tasks if t.division_id == self.division_id]
        ok = 0
        revenue = 0.0
        notes: list[str] = []
        self.last_results = []
        # round-robin tasks across workers
        for i, task in enumerate(mine):
            if not self._workers:
                notes.append(f"no workers registered for {self.division_id}")
                break
            worker = self._workers[i % len(self._workers)]
            result = worker.execute(task)
            self.last_results.append(result)
            if result.status == "ok":
                ok += 1
                revenue += result.mock_revenue_usd
            else:
                notes.append(f"{worker.worker_id}: {result.notes[:80]}")
        return DivisionReport(
            division_id=self.division_id,
            division_name=self.division_name,
            workers_run=len(mine),
            workers_ok=ok,
            mock_revenue_usd=round(revenue, 2),
            notes=notes,
        )
