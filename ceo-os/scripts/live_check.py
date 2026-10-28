#!/usr/bin/env python3
"""Live verification for CEO-OS (run the moment MODEL_API_KEY exists).

One tiny call only — this checks the live path without burning credits:
- builds MetaProvider (fails LOUDLY without a key, never fake-passes)
- sends one short prompt, prints latency + token counts from provider.health()
- prints the spend warning: Meta's Spend Limit is an alert, NOT a hard cap,
  so keep live runs small and watched until credits are confirmed in Billing.

Usage:
    cd ceo-os
    MODEL_API_KEY=<redacted> PYTHONPATH=src python3 scripts/live_check.py
Without a key it prints SKIP (not PASS) and exits 0 — the demo stays mock.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ceo_os.meta_provider import MetaProvider, MissingKeyError


def main() -> int:
    if not (os.environ.get("MODEL_API_KEY") or os.environ.get("META_MODEL_API_KEY")):
        print("[live-check] SKIP: no MODEL_API_KEY in environment.")
        print("[live-check] Boss: create the key at dev.meta.ai after credits land,")
        print("[live-check] then re-run this script. Nothing was called, $0 spent.")
        return 0
    try:
        provider = MetaProvider(reasoning_effort="minimal")
    except MissingKeyError as e:
        print(f"[live-check] SKIP: {e}")
        return 0
    print(f"[live-check] LIVE provider: {provider.model} via {provider.base_url}")
    print("[live-check] WARNING: Meta Spend Limit is an alert, not a hard cap.")
    t0 = time.time()
    out = provider.complete("Reply in 5 words: what does CEO-OS do?", max_tokens=30)
    dt = time.time() - t0
    print(f"[live-check] reply: {out}")
    print(f"[live-check] latency: {dt:.1f}s | health: {provider.health()}")
    print("[live-check] PASS: live Muse Spark path works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
