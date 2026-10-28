"""Creator Studio tests — offline, mock provider only.

Run: python3 tests/test_creator.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOSS_HOME = os.environ.get("BOSS_CEO_HOME",
                           os.path.expanduser("~/workspace/boss-ceo"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, BOSS_HOME)

from src.mock.provider import MockLLMProvider  # noqa: E402
from src.divisions.manager import DivisionManagerBase  # noqa: E402
from src.contracts.models import Task  # noqa: E402
from creator_workers import ROSTER  # noqa: E402

ALLOWED_GATES = {"ok", "post it", "upload it", "send", "go", None}


def test_roster_is_6_with_gates():
    assert len(ROSTER) == 6, f"workers: {len(ROSTER)}"
    for cls in ROSTER:
        assert getattr(cls, "task_kind", None), cls.__name__
        assert getattr(cls, "requires_gate", "MISSING") in ALLOWED_GATES, cls.__name__


def test_publish_prep_never_marks_ready():
    from creator_workers import PublishPrep
    llm = MockLLMProvider()
    w = PublishPrep("CRT-PublishPrep", "b1", "CRT", "PublishPrep", llm)
    result = w.execute(Task(task_id="t1", business_id="b1",
                            division_id="CRT", kind="publish_prep",
                            payload={"topic": "x"}))
    assert result.status == "ok"
    assert result.output.get("ready_to_publish") is False
    assert result.output.get("gate") == "post it"


def test_full_studio_run_all_ok_mock():
    llm = MockLLMProvider()
    mgr = DivisionManagerBase("CRT", "Creator Studio")
    for cls in ROSTER:
        mgr.register_worker(cls(f"CRT-{cls.__name__}", "b1", "CRT",
                                cls.__name__, llm))
    tasks = [Task(task_id=f"t{i}", business_id="b1", division_id="CRT",
                  kind=getattr(w, "task_kind", "x"),
                  payload={"topic": "test", "format": "short video",
                           "niche": "test"})
             for i, w in enumerate(mgr.workers)]
    rep = mgr.dispatch(tasks)
    assert rep.workers_run == 6 and rep.workers_ok == 6
    gates = [r.output.get("gate") for r in mgr.last_results]
    assert "post it" in gates  # publish waits for the owner


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
    print(f"{passed}/{len(tests)} creator tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
