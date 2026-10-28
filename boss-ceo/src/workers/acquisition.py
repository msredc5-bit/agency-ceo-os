"""ACQ division workers — Boss's SDR team (his standing rules baked in)."""
from __future__ import annotations

from src.contracts.models import Task
from src.workers.base import WorkerBase


class ProspectResearcher(WorkerBase):
    """Finds US home-service SMBs with pain signals (his tx-prospects pattern)."""
    task_kind = "prospect_research"
    default_payload = {"niche": "plumbing", "region": "Texas"}
    requires_gate = None  # research only, nothing goes out

    def do_work(self, task: Task) -> tuple[str, dict]:
        niche = task.payload.get("niche", "plumbing")
        region = task.payload.get("region", "Texas")
        plan = self.llm.complete(
            f"Research 10 {niche} SMBs in {region}: owner name, missed-call pain "
            f"signals, tech gaps, personalization angle. No dental/medical."
        )
        return plan, {"niche": niche, "region": region, "prospects": 10,
                      "fields": ["name", "owner", "pain_signals", "angle"]}


class OutreachDrafter(WorkerBase):
    """Drafts cold emails/DMs. Drafts ONLY — sending is Boss's 'send' gate."""
    task_kind = "outreach_draft"
    default_payload = {"channel": "email"}
    requires_gate = "send"

    def do_work(self, task: Task) -> tuple[str, dict]:
        channel = task.payload.get("channel", "email")  # email | instagram
        limit = "20-30/day, personalized" if channel == "email" else "5-10/day warm-up"
        sender = "hello@talvenorai.agency" if channel == "email" else "@talvenor_ai"
        plan = self.llm.complete(
            f"Draft 5 {channel} outreach messages ({limit}) from {sender}. "
            f"Short, plain US English, one CTA: short call. No prices, no guarantees, "
            f"no invented clients. Hook first."
        )
        return plan, {"channel": channel, "drafts": 5, "from": sender,
                      "gate": "send", "note": "DRAFT ONLY — Boss sends"}


class ReplyHandler(WorkerBase):
    """Triage prospect replies per the locked 2026-10-14 reply rule."""
    task_kind = "reply_triage"
    default_payload = {"reply_type": "interest"}
    requires_gate = "send"  # interest replies need Boss's eyes before anything sends

    def do_work(self, task: Task) -> tuple[str, dict]:
        reply_type = task.payload.get("reply_type", "interest")
        if reply_type == "decline":
            action = ("polite exit (allowed to send): thank them, leave the door "
                      "open, no pitch")
            gate = None
        else:  # interest / question / pricing / demo request
            action = ("DRAFT ONLY, never send: answer briefly, no prices quoted "
                      "(offer a short call instead), flag Boss with name+platform+message")
            gate = "send"
        plan = self.llm.complete(f"Prospect reply triage [{reply_type}]: {action}")
        return plan, {"reply_type": reply_type, "action": action, "gate": gate}


class NegotiationCoach(WorkerBase):
    """Prepares the founder for the live sales call (hackathon worker)."""
    task_kind = "negotiation_prep"
    default_payload = {"prospect": "", "goal": "book the demo call"}
    requires_gate = "ok"

    def do_work(self, task: Task) -> tuple[str, dict]:
        prospect = task.payload.get("prospect", "")
        goal = task.payload.get("goal", "book the demo call")
        plan = self.llm.complete(
            f"Given prospect profile [{prospect}] and call goal [{goal}], produce: "
            f"3 likely questions with strong answers, 2 traps to avoid, and a "
            f"60-second opening script in plain US English. Flag anything that "
            f"needs the founder's decision as GATE. No prices quoted."
        )
        return plan, {"gate": "ok", "note": "PREP ONLY — Boss takes the call"}
