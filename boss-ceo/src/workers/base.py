"""Layer 3 — WorkerBase: template every micro-business worker extends.

Concrete workers override `do_work()`; the base handles result wrapping,
failure capture, and mock-revenue parsing so no worker ever raises.
"""
from __future__ import annotations

import re

from src.contracts.llm import LLMProvider
from src.contracts.models import Task, WorkerResult
from src.contracts.worker import Worker


class WorkerBase(Worker):
    def __init__(
        self,
        worker_id: str,
        business_id: str,
        division_id: str,
        display_name: str,
        llm: LLMProvider,
    ):
        self.worker_id = worker_id
        self.business_id = business_id
        self.division_id = division_id
        self.display_name = display_name
        self.llm = llm

    # -- override this in concrete workers ---------------------------------
    def do_work(self, task: Task) -> tuple[str, dict]:
        """Return (notes, output_dict). May use self.llm.complete()."""
        text = self.llm.complete(
            f"[{self.display_name}] execute {task.kind}: {task.payload}"
        )
        return text, {"plan": text}

    # -- base machinery (do not override) ----------------------------------
    def execute(self, task: Task) -> WorkerResult:
        try:
            notes, output = self.do_work(task)
            revenue = self._parse_mock_revenue(notes)
            return WorkerResult(
                worker_id=self.worker_id,
                task_id=task.task_id,
                status="ok",
                output=output,
                mock_revenue_usd=revenue,
                notes=notes[:280],
            )
        except Exception as exc:  # never let a worker crash the day
            return WorkerResult(
                worker_id=self.worker_id,
                task_id=task.task_id,
                status="failed",
                notes=f"worker error: {exc}"[:280],
            )

    @staticmethod
    def _parse_mock_revenue(notes: str) -> float:
        m = re.search(r"\$(\d+(?:\.\d{1,2})?)", notes)
        return float(m.group(1)) if m else 0.0
