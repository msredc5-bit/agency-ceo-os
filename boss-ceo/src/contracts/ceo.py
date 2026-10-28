"""Layer 0 — CEO interface. The orchestrator: plans, delegates, aggregates, reports."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .division import DivisionManager
from .models import DayReport


class CEO(ABC):
    @abstractmethod
    def register_division(self, division: DivisionManager) -> None: ...

    @abstractmethod
    def run_day(self, date: str) -> DayReport:
        """Execute one full business day across all divisions (mock or live)."""

    @abstractmethod
    def chairman_brief(self, report: DayReport) -> str:
        """Render the human-readable Chairman report."""
