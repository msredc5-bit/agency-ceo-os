"""Layer 2 — CEO orchestrator: plans the day, delegates to divisions,
aggregates reports, writes the ledger, renders the Chairman brief.

All money figures are MOCK (demo ledger only). No live execution paths exist
in this shell — those arrive per-division with explicit approval.
"""
from __future__ import annotations

from collections.abc import Callable

from src.contracts.ceo import CEO
from src.contracts.division import DivisionManager
from src.contracts.llm import LLMProvider
from src.contracts.models import DayReport, LedgerEntry, Task, utcnow
from src.contracts.store import Store
from src.divisions.manager import DivisionManagerBase
from src.workers.base import WorkerBase

# Signature: (worker_id, business_id, division_id, display_name, llm) -> WorkerBase
WorkerFactory = Callable[[str, str, str, str, LLMProvider], WorkerBase]


def default_worker_factory(
    worker_id: str, business_id: str, division_id: str,
    display_name: str, llm: LLMProvider,
) -> WorkerBase:
    return WorkerBase(worker_id, business_id, division_id, display_name, llm)


class CEOOrchestrator(CEO):
    def __init__(self, llm: LLMProvider, store: Store,
                 worker_factory: WorkerFactory = default_worker_factory):
        self.llm = llm
        self.store = store
        self.worker_factory = worker_factory
        self._divisions: list[DivisionManager] = []

    def register_division(self, division: DivisionManager) -> None:
        self._divisions.append(division)

    def build_division(self, division_id: str, division_name: str,
                       businesses: list[dict]) -> DivisionManagerBase:
        """Instantiate a division + one worker per business from registry data."""
        mgr = DivisionManagerBase(division_id, division_name)
        for i, biz in enumerate(businesses):
            wid = f"{division_id}-w{i+1:02d}"
            mgr.register_worker(self.worker_factory(
                wid, biz["business_id"], division_id,
                biz.get("name", wid), self.llm,
            ))
        return mgr

    def build_tasks(self, date: str) -> list[Task]:
        """One generic task per worker. Subclasses override for specialty tasks."""
        tasks: list[Task] = []
        for div in self._divisions:
            for i in range(div.worker_count()):
                bid = f"{div.division_id}-biz-{i+1:02d}"
                task = Task(
                    task_id=f"{date}-{div.division_id}-{i+1:02d}",
                    business_id=bid,
                    division_id=div.division_id,
                    kind="mock_revenue_check",
                    payload={"mode": "mock_day"},
                )
                tasks.append(task)
        return tasks

    def run_day(self, date: str) -> DayReport:
        tasks = self.build_tasks(date)

        reports = []
        all_results = []
        for div in self._divisions:
            rep = div.dispatch(tasks)
            reports.append(rep)
            all_results.extend(getattr(div, "last_results", []))
        # batch persist (single transactions at scale)
        if hasattr(self.store, "save_tasks_batch"):
            self.store.save_tasks_batch(tasks)
            self.store.save_results_batch(all_results)
        else:
            for t in tasks:
                self.store.save_task(t)
            for r in all_results:
                self.store.save_result(r)
        for rep in reports:
            self.store.save_ledger(LedgerEntry(
                entry_id=f"{date}-{rep.division_id}",
                kind="mock_revenue",
                amount_usd=rep.mock_revenue_usd,
                division_id=rep.division_id,
                memo=f"Mock day revenue — {rep.division_name}",
            ))

        # CEO's own planning note via the LLM (mock in this shell)
        self.llm.complete(f"CEO daily plan for {date}: {len(tasks)} tasks")

        report = DayReport(
            date=date,
            divisions_run=len(reports),
            workers_run=sum(r.workers_run for r in reports),
            workers_ok=sum(r.workers_ok for r in reports),
            mock_revenue_usd=round(sum(r.mock_revenue_usd for r in reports), 2),
            mock_cost_usd=0.0,
            division_reports=reports,
        )
        self.store.save_day_report(report)
        return report

    def chairman_brief(self, report: DayReport) -> str:
        lines = [
            "=" * 56,
            f"CHAIRMAN BRIEF — {report.date} (MOCK DATA, $0 spend)",
            "=" * 56,
            f"Divisions run : {report.divisions_run}",
            f"Workers run   : {report.workers_run}  (ok: {report.workers_ok})",
            f"Mock revenue  : ${report.mock_revenue_usd:,.2f}",
            f"Mock cost     : ${report.mock_cost_usd:,.2f}  (mock LLM = $0)",
            "-" * 56,
        ]
        for r in report.division_reports:
            lines.append(
                f"{r.division_id} {r.division_name[:34]:<34} "
                f"ok {r.workers_ok}/{r.workers_run}  ${r.mock_revenue_usd:>8.2f}"
            )
        lines.append("=" * 56)
        return "\n".join(lines)
