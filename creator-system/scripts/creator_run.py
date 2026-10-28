#!/usr/bin/env python3
"""Creator Studio demo: one command runs the content-creation system.

Flow: CEO decision -> research -> script -> visual -> caption
      -> publish prep (GATE) -> performance report.

Usage:
  python3 scripts/creator_run.py [--niche "cooking"] [--topic ""] \
      [--format "short video"] [--report-json out.json]

$0 spend. Mock data only. Nothing publishes, sends, or leaves this machine.
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOSS_HOME = os.environ.get(
    "BOSS_CEO_HOME", os.path.expanduser("~/workspace/boss-ceo"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, BOSS_HOME)

from src.ceo.orchestrator import CEOOrchestrator  # noqa: E402
from src.divisions.manager import DivisionManagerBase  # noqa: E402
from src.mock.provider import MockLLMProvider  # noqa: E402
from src.store.db import SQLiteStore  # noqa: E402
from creator_workers import ROSTER  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=str(date.today()))
    ap.add_argument("--db", default="data/creator-studio.db")
    ap.add_argument("--niche", default="general")
    ap.add_argument("--topic", default="")
    ap.add_argument("--format", default="short video")
    ap.add_argument("--report-json", default="")
    args = ap.parse_args()

    llm = MockLLMProvider(seed="creator-studio-v1")
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    store = SQLiteStore(str(ROOT / args.db))
    store.init()

    # Step 1 — CEO decision (the step Boss asked for first)
    decision = llm.complete(
        f"CEO decision: creator niche '{args.niche}', topic "
        f"'{args.topic or 'to be chosen by research'}', format "
        f"'{args.format}'. Decide: go or not, and in one line why."
    )
    print("=" * 58)
    print("CREATOR STUDIO — CEO DECISION (MOCK, $0)")
    print("=" * 58)
    print(decision)
    print()

    # Step 2 — the studio runs: research -> script -> visual -> caption
    # -> publish prep -> performance report
    ceo = CEOOrchestrator(llm=llm, store=store)
    mgr = DivisionManagerBase("CRT", "Creator Studio")
    for cls in ROSTER:
        mgr.register_worker(cls(
            f"CRT-{cls.__name__}", "creator-biz-01", "CRT",
            cls.__name__, llm))
    ceo.register_division(mgr)

    # Specialty tasks: every worker gets the same topic/format payload.
    from src.contracts.models import Task
    tasks = []
    for w in mgr.workers:
        kind = getattr(w, "task_kind", "mock_revenue_check")
        tasks.append(Task(
            task_id=f"{args.date}-{w.worker_id}",
            business_id=w.business_id,
            division_id="CRT",
            kind=kind,
            payload={"niche": args.niche, "topic": args.topic,
                     "format": args.format},
        ))
    rep = mgr.dispatch(tasks)
    print(f"Studio run: {rep.workers_ok}/{rep.workers_run} workers ok")
    for note in rep.notes:
        print("  -", note)

    # Step 3 — gates: publish waits for the owner's exact word
    gates = []
    for r in mgr.last_results:
        gate = (r.output or {}).get("gate")
        if gate:
            gates.append({"worker": r.worker_id, "gate": gate})
    print()
    print(f"Pending gates: {len(gates)} (none auto-advanced)")
    for g in gates:
        print(f"  - [{g['worker']}] gate='{g['gate']}'")
    print()
    print(f"mock LLM calls: {llm.calls} | spend: $0.00")

    if args.report_json:
        payload = {
            "date": args.date,
            "system": "creator-studio",
            "mode": "mock",
            "niche": args.niche,
            "topic": args.topic,
            "format": args.format,
            "workers_run": rep.workers_run,
            "workers_ok": rep.workers_ok,
            "pending_gates": gates,
            "provider_health": llm.health(),
            "note": "Mock data only. Publish gate waits for the owner's word.",
        }
        with open(args.report_json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"day report JSON: {args.report_json}")


if __name__ == "__main__":
    main()
