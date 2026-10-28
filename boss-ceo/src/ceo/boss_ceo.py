"""BossCEO — the chairman's personal CEO agent.

Customized from Boss's profile (config/boss.yaml):
- Knows his 4 real divisions and 11 workers (not 50 generic ones)
- Enforces his approval gates IN CODE: gated task kinds are reported as
  'awaiting Boss' and never auto-advanced
- Chairman brief in Bengali (his language), $0 spend, mock-first
"""
from __future__ import annotations

import yaml

from src.ceo.orchestrator import CEOOrchestrator
from src.contracts.models import DayReport
from src.store.db import SQLiteStore
from src.mock.provider import MockLLMProvider

GATE_WORDS = {
    "ok": "পরিকল্পনা/অ্যাসেট অনুমোদন",
    "post it": "পাবলিশ",
    "upload it": "ভিডিও আপলোড",
    "send": "পাঠানো (মেসেজ/ইমেইল)",
    "go": "বিল্ড এগিয়ে নেওয়া",
}


class BossCEO(CEOOrchestrator):
    def __init__(self, llm=None, store=None, profile_path="config/boss.yaml"):
        llm = llm or MockLLMProvider(seed="boss-ceo-v1")
        store = store or SQLiteStore("data/boss-ceo.db")
        super().__init__(llm, store)
        with open(profile_path, encoding="utf-8") as f:
            self.profile = yaml.safe_load(f)
        self.chairman_name = self.profile["chairman"]["title"]

    def build_tasks(self, date: str) -> list[Task]:
        """One specialty task per worker: each worker's own task_kind + payload."""
        from src.contracts.models import Task
        tasks: list[Task] = []
        for div in self._divisions:
            for w in div.workers:
                kind = getattr(w, "task_kind", "mock_revenue_check")
                payload = getattr(w, "default_payload", {})
                tasks.append(Task(
                    task_id=f"{date}-{w.worker_id}",
                    business_id=w.business_id,
                    division_id=div.division_id,
                    kind=kind,
                    payload=dict(payload),
                ))
        return tasks

    def pending_gates(self, report: DayReport) -> list[dict]:
        """Collect every worker output that needs Boss's exact word."""
        pending = []
        for div in self._divisions:
            for r in getattr(div, "last_results", []):
                gate = (r.output or {}).get("gate")
                if gate:
                    pending.append({
                        "division": div.division_id,
                        "worker": r.worker_id,
                        "gate": gate,
                        "meaning": GATE_WORDS.get(gate, gate),
                        "summary": r.notes[:90],
                    })
        return pending

    def chairman_brief(self, report: DayReport) -> str:
        p = self.profile
        L = [
            "=" * 58,
            f"চেয়ারম্যান ব্রিফ — {report.date}  ({p['company']['name']} · {self.chairman_name})",
            "mock data · $0 খরচ · কিছুই live হয়নি",
            "=" * 58,
            f"ডিভিশন: {report.divisions_run} · ওয়ার্কার: {report.workers_run} "
            f"(সফল: {report.workers_ok})",
            "-" * 58,
        ]
        for r in report.division_reports:
            L.append(f"[{r.division_id}] {r.division_name[:30]:<30} "
                     f"ok {r.workers_ok}/{r.workers_run}")
        gates = self.pending_gates(report)
        L.append("-" * 58)
        if gates:
            L.append(f"⏳ অপেক্ষমাণ অনুমোদন ({len(gates)}টি) — তোমার সিদ্ধান্ত লাগবে:")
            for g in gates:
                L.append(f"  [{g['division']}] {g['worker']}")
                L.append(f"    gate: '{g['gate']}' ({g['meaning']})")
        else:
            L.append("✅ কোনো অনুমোদন বাকি নেই।")
        L.append("=" * 58)
        L.append("নিয়ম: 'ok'/'post it'/'upload it'/'send'/'go' — সঠিক শব্দ ছাড়া কিছু এগোবে না।")
        return "\n".join(L)
