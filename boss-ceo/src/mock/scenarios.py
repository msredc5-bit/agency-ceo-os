"""Layer 1 — scenario runner: scripted mock days for repeatable demos/tests."""
from __future__ import annotations

from src.contracts.models import Task


def demo_day_tasks(division_ids: list[str], workers_per_division: int = 3) -> list[Task]:
    """Build a deterministic task list: one mock task per worker slot."""
    tasks: list[Task] = []
    for did in division_ids:
        for i in range(workers_per_division):
            bid = f"{did}-biz-{i+1:02d}"
            tasks.append(
                Task(
                    task_id=f"demo-{did}-{i+1:02d}",
                    business_id=bid,
                    division_id=did,
                    kind="mock_revenue_check",
                    payload={"slot": i + 1, "mode": "demo"},
                )
            )
    return tasks
