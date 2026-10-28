#!/usr/bin/env python3
"""Boss CEO demo: one command runs Boss's personal CEO agent.

Usage: python3 scripts/boss_run.py [--date YYYY-MM-DD] [--db data/boss-ceo.db]

$0 spend. Mock data only. Nothing leaves this machine.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from src.ceo.boss_ceo import BossCEO  # noqa: E402
from src.divisions.manager import DivisionManagerBase  # noqa: E402
from src.mock.provider import MockLLMProvider  # noqa: E402
from src.store.db import SQLiteStore  # noqa: E402
from src.workers.acquisition import ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach  # noqa: E402
from src.workers.delivery import RetellBuilder, QAEngineer, OnboardingAgent  # noqa: E402
from src.workers.marketing import ContentPlanner, VideoProducer, CaptionWriter, PublishPrep, ObjectionSimulator  # noqa: E402
from src.workers.admin import InboxTriager, ReportCompiler, SchedulerAssistant  # noqa: E402

ROSTER = {
    ("ACQ", "Client Acquisition"): [
        ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach],
    ("DEL", "Receptionist Delivery"): [
        RetellBuilder, QAEngineer, OnboardingAgent],
    ("MKT", "Marketing & Content"): [
        ContentPlanner, VideoProducer, CaptionWriter, PublishPrep,
        ObjectionSimulator],
    ("OPS", "Operations & Admin"): [
        InboxTriager, ReportCompiler, SchedulerAssistant],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=str(date.today()))
    ap.add_argument("--db", default="data/boss-ceo.db")
    args = ap.parse_args()

    llm = MockLLMProvider(seed="boss-ceo-v1")
    store = SQLiteStore(str(ROOT / args.db))
    store.init()
    ceo = BossCEO(llm=llm, store=store,
                  profile_path=str(ROOT / "config" / "boss.yaml"))
    # sanity: profile gates match the CEO's gate words
    assert set(yaml.safe_load(
        open(ROOT / "config" / "boss.yaml", encoding="utf-8"))["gates"]) >= \
        {"ok", "post it", "upload it", "send", "go"}

    for (did, dname), workers in ROSTER.items():
        mgr = DivisionManagerBase(did, dname)
        for i, cls in enumerate(workers):
            wid = f"{did}-{cls.__name__}"
            mgr.register_worker(cls(wid, f"{did}-biz-{i+1:02d}", did,
                                    cls.__name__, llm))
        ceo.register_division(mgr)

    report = ceo.run_day(args.date)
    print(ceo.chairman_brief(report))
    print()
    print(f"mock LLM calls: {llm.calls} | spend: $0.00")


if __name__ == "__main__":
    main()
