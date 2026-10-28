"""CEO-OS — Meta Model API provider layer.

The hackathon core: plugs Meta's Muse Spark models into the CEO-OS
orchestrator through the existing LLMProvider seam. One-line swap:

    from ceo_os.meta_provider import build_provider
    ceo = BossCEO(llm=build_provider())   # live Muse Spark, or loud mock fallback

Verified API facts (Meta Model API docs, Oct 2026):
- Base URL: https://api.meta.ai/v1 (OpenAI-compatible)
- Endpoint: POST /chat/completions
- Auth: Authorization: Bearer $MODEL_API_KEY
- Model IDs: muse-spark-1.3 / muse-spark-1.2 / muse-spark-1.1
- Context: 1,048,576 tokens. reasoning_effort: minimal..xhigh ("none" returns 400)
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "https://api.meta.ai/v1"
DEFAULT_MODEL = "muse-spark-1.3"

# Cost: tracked as tokens only. We do NOT invent $ pricing — see
# https://dev.meta.ai/docs for current Meta Model API pricing.
PRICING_NOTE = "token counts only; $ cost needs Meta's current price sheet"


class MissingKeyError(RuntimeError):
    """Raised when MetaProvider is constructed without an API key."""


class MetaProvider:
    """LLMProvider backed by Meta Model API (Muse Spark series)."""

    name = "meta"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        reasoning_effort: str = "low",
        timeout_s: int = 60,
        max_retries: int = 3,
    ):
        key = api_key or os.environ.get("MODEL_API_KEY") or os.environ.get("META_MODEL_API_KEY")
        if not key:
            raise MissingKeyError(
                "No Meta Model API key. Set MODEL_API_KEY (or META_MODEL_API_KEY) "
                "in your environment — hackathon participants get $150 in credits. "
                "See .env.example."
            )
        self.api_key = key
        self.model = model or os.environ.get("META_MODEL", DEFAULT_MODEL)
        self.base_url = (base_url or os.environ.get("META_MODEL_API_BASE", DEFAULT_BASE_URL)).rstrip("/")
        if reasoning_effort not in ("minimal", "low", "medium", "high", "xhigh"):
            raise ValueError("reasoning_effort must be minimal|low|medium|high|xhigh (Muse Spark rejects 'none')")
        self.reasoning_effort = reasoning_effort
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        # usage ledger — every call logged, honest numbers only
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.failures = 0

    # -- LLMProvider interface -------------------------------------------------
    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": (
                    "You are a specialist worker inside CEO-OS, a personal CEO agent "
                    "for a solo founder. Follow the brief exactly. Be concise and concrete. "
                    "Never invent numbers, clients, prices, or results — if a number is "
                    "needed and not given, say what input is missing."
                )},
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": max_tokens,
            "reasoning_effort": self.reasoning_effort,
            "temperature": 0.3,
        }
        data = json.dumps(body).encode()
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/chat/completions",
                    data=data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    payload = json.loads(resp.read().decode())
                return self._handle_response(payload)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                last_err = e
                self.failures += 1
                time.sleep(2 ** attempt)  # backoff: 1s, 2s, 4s
        raise RuntimeError(f"Meta Model API failed after {self.max_retries} attempts: {last_err}")

    def _handle_response(self, payload: dict) -> str:
        if "error" in payload:
            raise RuntimeError(f"Meta Model API error: {payload['error']}")
        choice = payload["choices"][0]
        text = choice["message"].get("content") or ""
        usage = payload.get("usage", {})
        self.calls += 1
        self.prompt_tokens += int(usage.get("prompt_tokens", 0))
        self.completion_tokens += int(usage.get("completion_tokens", 0))
        return text.strip()

    def health(self) -> dict:
        return {
            "provider": self.name,
            "model": self.model,
            "ok": True,
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "failures": self.failures,
            "pricing": PRICING_NOTE,
        }


def build_provider(reasoning_effort: str = "low"):
    """Live MetaProvider when a key exists, else a LOUD mock fallback.

    Never silently fakes live intelligence: the fallback prints exactly
    what it is, so a demo can't be mistaken for a Muse Spark run.
    """
    try:
        provider = MetaProvider(reasoning_effort=reasoning_effort)
        print(f"[ceo-os] LIVE provider: {provider.model} via {provider.base_url}")
        return provider
    except MissingKeyError as e:
        print(f"[ceo-os] WARNING: {e}")
        print("[ceo-os] Falling back to deterministic MOCK provider ($0, offline).")
        print("[ceo-os] Set MODEL_API_KEY to run on real Muse Spark models.")
        import sys
        sys.path.insert(0, os.environ.get("BOSS_CEO_HOME", os.path.expanduser("~/workspace/boss-ceo")))
        from src.mock.provider import MockLLMProvider
        return MockLLMProvider(seed="ceo-os-hackathon")
