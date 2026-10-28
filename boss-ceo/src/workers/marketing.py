"""MKT division workers — the weekly content engine (Division C SOPs)."""
from __future__ import annotations

from src.contracts.models import Task
from src.workers.base import WorkerBase


class ContentPlanner(WorkerBase):
    """Sunday 6 PM Dhaka: next week's 5-post plan across FB/IG/LinkedIn."""
    task_kind = "content_plan"
    requires_gate = "ok"

    def do_work(self, task: Task) -> tuple[str, dict]:
        plan = self.llm.complete(
            "Weekly 5-post plan: pillars (missed-call pain, AI receptionist demo, "
            "founder voice, social proof w/o invented clients, CTA). Per post: "
            "platform, format, hook, best US-Eastern time. Wait for Boss 'ok'."
        )
        return plan, {"posts": 5, "platforms": ["facebook", "instagram", "linkedin"],
                      "cadence": "Sunday 6PM Dhaka", "gate": "ok"}


class VideoProducer(WorkerBase):
    """Produces reels per the reel-factory SOP: real footage first, never stills-motion."""
    task_kind = "video_produce"
    default_payload = {"topic": "missed call = lost job"}
    requires_gate = "ok"

    def do_work(self, task: Task) -> tuple[str, dict]:
        topic = task.payload.get("topic", "missed call = lost job")
        plan = self.llm.complete(
            f"Reel package for '{topic}': hook in first 2s, real footage (frame-"
            f"verified), US-English voiceover, karaoke captions, Talvenor end card "
            f"(wave logo, never redrawn), 'Illustrative example' on hypotheticals. "
            f"Gate 'upload it' before anything publishes."
        )
        return plan, {"topic": topic, "format": "9:16", "spec": "reel-factory",
                      "gate": "ok"}


class CaptionWriter(WorkerBase):
    """Caption + hashtag + CTA pack per finished creative (caption-pack SOP)."""
    task_kind = "caption_write"
    default_payload = {"platform": "instagram"}
    requires_gate = None  # ships with the asset; publish still gated

    def do_work(self, task: Task) -> tuple[str, dict]:
        platform = task.payload.get("platform", "instagram")
        plan = self.llm.complete(
            f"Caption pack ({platform}): hook first line, plain US English, one CTA "
            f"('link in bio' only when a real booking link exists), hashtags "
            f"(IG 5-8 / LinkedIn 3 / FB 0-2). No prices, no guarantees."
        )
        return plan, {"platform": platform, "includes": ["caption", "hashtags", "cta"]}


class PublishPrep(WorkerBase):
    """Prepares approved posts for publishing. NEVER publishes itself."""
    task_kind = "publish_prep"
    default_payload = {"count": 2}
    requires_gate = "post it"

    def do_work(self, task: Task) -> tuple[str, dict]:
        n = task.payload.get("count", 1)
        plan = self.llm.complete(
            f"Prepare {n} post(s) for publishing: final file + caption + first "
            f"comment + scheduled time (US Eastern). Publishing runs ONLY from the "
            f"main chat after Boss says 'post it'. Detached auto-publish is banned "
            f"(2026-10-10 lesson)."
        )
        return plan, {"count": n, "gate": "post it",
                      "note": "PREPARE ONLY — Boss publishes"}


class ObjectionSimulator(WorkerBase):
    """Plays the skeptical prospect before real outreach goes out (hackathon worker)."""
    task_kind = "objection_sim"
    default_payload = {"draft": "", "prospect": ""}
    requires_gate = "ok"  # review output; outreach itself still needs 'send'

    def do_work(self, task: Task) -> tuple[str, dict]:
        draft = task.payload.get("draft", "")
        prospect = task.payload.get("prospect", "")
        plan = self.llm.complete(
            f"Given outreach draft [{draft}] and prospect profile [{prospect}], "
            f"play the skeptical prospect. List the 5 most likely objections in "
            f"the prospect's own words, ranked by likelihood, each with a one-line "
            f"rebuttal angle. Be harsh — a weak draft must not survive this review. "
            f"No invented clients or prices."
        )
        return plan, {"gate": "ok", "note": "REVIEW ONLY — never sent to a prospect"}
