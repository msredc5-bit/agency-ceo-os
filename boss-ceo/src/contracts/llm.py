"""Layer 0 — LLMProvider interface.

The single seam that makes 'plug in API keys later' work:
implementations: MockLLMProvider (Layer 1, $0) -> OllamaProvider (optional,
local) -> ClaudeProvider / GPTProvider (live, added later with approval).
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        """Return a completion for the prompt. Must be deterministic given
        the same prompt when the provider is in mock mode."""

    def health(self) -> dict:
        return {"provider": self.name, "ok": True}
