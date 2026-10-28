"""Engine tests for boss-ceo — all offline, mock provider only.

Run without pytest:  python3 tests/test_engine.py
"""
from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.ceo.boss_ceo import BossCEO  # noqa: E402
from src.divisions.manager import DivisionManagerBase  # noqa: E402
from src.mock.provider import MockLLMProvider  # noqa: E402
from src.store.db import SQLiteStore  # noqa: E402
from src.workers.base import WorkerBase  # noqa: E402
from src.contracts.models import Task  # noqa: E402

ALLOWED_GATES = {"ok", "post it", "upload it", "send", "go", None}


def test_roster_is_15_workers_4_divisions():
    from scripts.boss_run import ROSTER
    total = sum(len(v) for v in ROSTER.values())
    assert len(ROSTER) == 4, f"divisions: {len(ROSTER)}"
    assert total == 15, f"workers: {total}"
    for workers in ROSTER.values():
        for cls in workers:
            assert getattr(cls, "task_kind", None), cls.__name__
            assert getattr(cls, "requires_gate", "MISSING") in ALLOWED_GATES, cls.__name__


def test_failing_worker_does_not_crash_day():
    llm = MockLLMProvider()

    class BoomWorker(WorkerBase):
        task_kind = "boom"
        requires_gate = "ok"

        def do_work(self, task):
            raise RuntimeError("boom")

    class GoodWorker(WorkerBase):
        task_kind = "good"
        requires_gate = "ok"

    mgr = DivisionManagerBase("TST", "Test")
    mgr.register_worker(BoomWorker("TST-boom", "b1", "TST", "Boom", llm))
    mgr.register_worker(GoodWorker("TST-good", "b2", "TST", "Good", llm))
    rep = mgr.dispatch([
        Task(task_id="t1", business_id="b1", division_id="TST", kind="boom"),
        Task(task_id="t2", business_id="b2", division_id="TST", kind="good"),
    ])
    assert rep.workers_run == 2
    assert rep.workers_ok == 1
    assert mgr.last_results[0].status == "failed"
    assert mgr.last_results[1].status == "ok"


def test_run_day_mock_cost_zero_and_brief_labelled_mock():
    with tempfile.TemporaryDirectory() as td:
        store = SQLiteStore(os.path.join(td, "t.db"))
        store.init()
        ceo = BossCEO(llm=MockLLMProvider(), store=store,
                      profile_path=os.path.join(ROOT, "config", "boss.yaml"))
        mgr = DivisionManagerBase("OPS", "Operations & Admin")
        from src.workers.admin import InboxTriager, ReportCompiler
        for cls in (InboxTriager, ReportCompiler):
            mgr.register_worker(cls(f"OPS-{cls.__name__}", "b1", "OPS", cls.__name__, ceo.llm))
        ceo.register_division(mgr)
        report = ceo.run_day("2026-01-01")
        assert report.mock_cost_usd == 0.0
        assert report.workers_run == 2 and report.workers_ok == 2
        brief = ceo.chairman_brief(report)
        assert "mock" in brief.lower()


def test_no_real_network_in_boss_ceo_src():
    banned = ("urllib", "requests.", "smtplib", "socket", "subprocess")
    src = os.path.join(ROOT, "src")
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            text = open(os.path.join(dirpath, fn), encoding="utf-8").read()
            for word in banned:
                assert word not in text, f"{fn} contains {word}"


def main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except Exception as exc:  # noqa: BLE001
            print("FAIL", name, type(exc).__name__, str(exc)[:160])
    print(f"{passed}/{len(tests)} engine tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
