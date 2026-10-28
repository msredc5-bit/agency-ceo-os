"""Layer 0 — Worker interface. One worker == one micro-business operator."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Task, WorkerResult


class Worker(ABC):
    worker_id: str
    business_id: str
    division_id: str
    display_name: str = "worker"

    @abstractmethod
    def execute(self, task: Task) -> WorkerResult:
        """Run one task for this worker's business. Must not raise:
        return WorkerResult(status='failed') instead."""
