"""Layer 1 — MockLLMProvider: deterministic $0 stand-in for Claude/GPT.

Same interface as the future live providers (contracts/llm.py), so swapping
is a config change. Responses are seeded by the prompt hash: same prompt in,
same text out, every run.
"""
from __future__ import annotations

import hashlib

from src.contracts.llm import LLMProvider

_TEMPLATES = [
    "MOCK-PLAN: assessed task '{hint}' — priority high, effort 2 units, "
    "expected mock revenue $38.50. Proceeding per division playbook.",
    "MOCK-PLAN: assessed task '{hint}' — priority normal, effort 1 unit, "
    "expected mock revenue $12.00. Proceeding per division playbook.",
    "MOCK-PLAN: assessed task '{hint}' — priority low, effort 1 unit, "
    "monitoring only, expected mock revenue $4.25.",
]


class MockLLMProvider(LLMProvider):
    name = "mock"

    def __init__(self, seed: str = "conglomerate-v1"):
        self.seed = seed
        self.calls = 0

    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        self.calls += 1
        digest = hashlib.sha256(f"{self.seed}|{prompt}".encode()).hexdigest()
        idx = int(digest[:8], 16) % len(_TEMPLATES)
        hint = " ".join(prompt.split())[:48]
        text = _TEMPLATES[idx].format(hint=hint)
        return text[:max_tokens]

    def health(self) -> dict:
        return {"provider": self.name, "ok": True, "calls": self.calls, "cost_usd": 0.0}
