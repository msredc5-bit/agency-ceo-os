"""DEL division workers — Talvenor receptionist delivery (Ava's lineage)."""
from __future__ import annotations

from src.contracts.models import Task
from src.workers.base import WorkerBase


class RetellBuilder(WorkerBase):
    """Builds a Retell receptionist from the prompt template (Ava v2 pattern)."""
    task_kind = "retell_build"
    default_payload = {"business": "Apex Plumbing", "trade": "plumbing"}
    requires_gate = "ok"

    def do_work(self, task: Task) -> tuple[str, dict]:
        business = task.payload.get("business", "Apex Plumbing")
        trade = task.payload.get("trade", "plumbing")
        plan = self.llm.complete(
            f"Build Retell receptionist for {business} ({trade}): self-sufficient "
            f"demo prompt — in-prompt schedule, emergency flow, callback handling, "
            f"FAQs, no invented pricing, fictional AP- confirmation numbers, "
            f"end_call only. Honest AI disclosure included."
        )
        return plan, {"business": business, "trade": trade,
                      "deliverables": ["agent-prompt", "knowledge-base", "recording-script"],
                      "gate": "ok"}


class QAEngineer(WorkerBase):
    """Runs the Retell QA checklist before any demo is called READY."""
    task_kind = "retell_qa"
    default_payload = {"agent": "ava-apex-plumbing-demo"}
    requires_gate = None  # checklist run; verdict still needs Boss's ok via G2

    def do_work(self, task: Task) -> tuple[str, dict]:
        agent = task.payload.get("agent", "ava-apex-plumbing-demo")
        plan = self.llm.complete(
            f"QA checklist for Retell agent {agent}: prompt completeness, "
            f"no broken tool references, emergency flow, pricing honesty, "
            f"transfer number real-or-absent, end_call behavior. Verdict: READY or CHANGES."
        )
        return plan, {"agent": agent, "checks": 12, "verdict": "READY-or-CHANGES"}


class OnboardingAgent(WorkerBase):
    """Drafts the client onboarding pack (info collection, not the build)."""
    task_kind = "onboarding_draft"
    default_payload = {"client": "new client"}
    requires_gate = "ok"

    def do_work(self, task: Task) -> tuple[str, dict]:
        client = task.payload.get("client", "new client")
        plan = self.llm.complete(
            f"Onboarding pack for {client}: business info form, hours/services/price "
            f"list request, transfer number confirmation, 7-day live guarantee terms "
            f"(3-month minimum, then month-to-month). No invented details."
        )
        return plan, {"client": client, "pack": ["info-form", "terms", "timeline"],
                      "gate": "ok"}
