"""CEO-OS end-to-end demo.

Runs the full engine (4 divisions, 15 workers) with the provider selected by
build_provider(): live Muse Spark when MODEL_API_KEY is set, loud mock
fallback otherwise. $0 spend, nothing goes live.

Usage:
    cd ceo-os
    PYTHONPATH=src python3 -m ceo_os.demo            # mock mode
    MODEL_API_KEY=... PYTHONPATH=src python3 -m ceo_os.demo   # live Muse Spark
"""
from __future__ import annotations

import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOSS_HOME = os.environ.get("BOSS_CEO_HOME", os.path.expanduser("~/workspace/boss-ceo"))
sys.path.insert(0, os.path.join(HERE, ".."))  # ceo_os package
sys.path.insert(0, BOSS_HOME)                 # boss-ceo engine

from ceo_os.meta_provider import build_provider
from ceo_os.briefs import NEW_WORKERS, build_brief

from src.ceo.boss_ceo import BossCEO
from src.divisions.manager import DivisionManagerBase
from src.store.db import SQLiteStore
from src.workers.acquisition import ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach
from src.workers.delivery import RetellBuilder, QAEngineer, OnboardingAgent
from src.workers.marketing import ContentPlanner, VideoProducer, CaptionWriter, PublishPrep, ObjectionSimulator
from src.workers.admin import InboxTriager, ReportCompiler, SchedulerAssistant

ROSTER = {
    ("ACQ", "Client Acquisition"): [ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach],
    ("DEL", "Receptionist Delivery"): [RetellBuilder, QAEngineer, OnboardingAgent],
    ("MKT", "Marketing & Content"): [ContentPlanner, VideoProducer, CaptionWriter, PublishPrep, ObjectionSimulator],
    ("OPS", "Operations & Admin"): [InboxTriager, ReportCompiler, SchedulerAssistant],
}


def main() -> int:
    provider = build_provider(reasoning_effort="low")

    data_dir = os.path.join(os.path.dirname(HERE), "data")
    os.makedirs(data_dir, exist_ok=True)
    store = SQLiteStore(os.path.join(data_dir, "ceo-os.db"))
    store.init()

    ceo = BossCEO(llm=provider, store=store,
                  profile_path=os.path.join(BOSS_HOME, "config", "boss.yaml"))
    for (did, dname), workers in ROSTER.items():
        mgr = DivisionManagerBase(did, dname)
        for i, cls in enumerate(workers):
            wid = f"{did}-{cls.__name__}"
            mgr.register_worker(cls(wid, f"{did}-biz-{i+1:02d}", did, cls.__name__, provider))
        ceo.register_division(mgr)

    today = datetime.date.today().isoformat()
    print(f"[ceo-os] Running CEO day: {today}")
    report = ceo.run_day(today)

    print()
    print(ceo.chairman_brief(report))
    print()
    gates = ceo.pending_gates(report)
    if gates:
        print(f"[ceo-os] Pending gates: {len(gates)} (all awaiting Boss — none auto-advanced)")
        for g in gates:
            print(f"  - [{g['division']}/{g['worker']}] gate='{g['gate']}' ({g['meaning']})")
    else:
        print("[ceo-os] No pending gates.")

    print()
    print("[ceo-os] Provider health:", provider.health())

    print()
    print("[ceo-os] Hackathon workers WIRED (no longer just briefs):")
    for wid, w in NEW_WORKERS.items():
        brief = build_brief(
            worker_role=w["role"], division=w["division"],
            company="Talvenor", task=w["task"],
            constraints="$0 spend. Never contact a real person.",
        )
        print(f"  - {wid} ({w['division']}): brief {len(brief)} chars, in roster: OK")

    print()
    print("[ceo-os] DONE — mock data · $0 খরচ · কিছুই live হয়নি")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
