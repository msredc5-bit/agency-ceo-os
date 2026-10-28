"""OPS division workers — the back office."""
from __future__ import annotations

from src.contracts.models import Task
from src.workers.base import WorkerBase


class InboxTriager(WorkerBase):
    """Triage inbox: sort, draft replies, flag what needs Boss. Sends nothing."""
    task_kind = "inbox_triage"
    requires_gate = None  # drafts only

    def do_work(self, task: Task) -> tuple[str, dict]:
        plan = self.llm.complete(
            "Triage inbox: urgent / prospect / vendor / noise. Draft replies in "
            "Boss's voice (short, plain). Anything with money, promises, or "
            "sending -> flag for Boss. Sends nothing."
        )
        return plan, {"drafts": True, "sends": False,
                      "note": "DRAFT ONLY — Boss sends"}


class ReportCompiler(WorkerBase):
    """Sunday performance report: visible metrics ONLY, never invented."""
    task_kind = "report_compile"
    requires_gate = None

    def do_work(self, task: Task) -> tuple[str, dict]:
        plan = self.llm.complete(
            "Weekly report: what was posted, best/worst by visible platform numbers "
            "only (if numbers unavailable, say so and ask Boss to paste them), "
            "leads list (name/platform/message/next step), what to change next week. "
            "Never estimate or invent metrics."
        )
        return plan, {"sections": ["posted", "performance", "leads", "next-week"],
                      "metrics_policy": "visible-only"}


class SchedulerAssistant(WorkerBase):
    """Scheduling help: finds times, drafts invites. Boss confirms."""
    task_kind = "schedule_help"
    default_payload = {"what": "client demo call"}
    requires_gate = None

    def do_work(self, task: Task) -> tuple[str, dict]:
        what = task.payload.get("what", "client call")
        plan = self.llm.complete(
            f"Schedule '{what}': propose 3 slots in Asia/Dhaka with US-Eastern "
            f"equivalents, draft the invite. Boss confirms before anything is sent."
        )
        return plan, {"what": what, "slots": 3, "tz": "Asia/Dhaka + US-Eastern"}
