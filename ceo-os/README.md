# CEO-OS — Personal CEO Agent for Solo Founders (Meta Hackathon Project)

**Track:** Indie developer · **Theme:** Build for Your World
**Status:** READY (mock mode, $0) → LIVE when `MODEL_API_KEY` is set
**2026-10-27 build update:** 15 workers live in the roster (13 original +
ObjectionSimulator + NegotiationCoach, wired, demo-verified). Live verification
is ready (`scripts/live_check.py`) but BLOCKED on the API key — Boss submitted
the $150 credit claim form 2026-10-27; credits land within 2 business days,
then he creates the key at dev.meta.ai and this script runs one tiny call.

## What it is

One orchestrator runs **15 specialist AI workers** across 4 divisions
(Client Acquisition, Delivery, Marketing, Operations). Approval gates are
enforced **in code** — anything that spends, publishes, or contacts a real
person is flagged `awaiting Boss` and never auto-advances. Numbers come from
deterministic Python tools, never from the model's imagination.

## The hackathon work (this repo)

`src/ceo_os/meta_provider.py` — `MetaProvider`, a drop-in `LLMProvider`
backed by **Meta Model API** (`POST https://api.meta.ai/v1/chat/completions`,
model `muse-spark-1.3`, OpenAI-compatible). One-line swap:

```python
from ceo_os.meta_provider import build_provider
ceo = BossCEO(llm=build_provider())   # live Muse Spark, or loud mock fallback
```

Without a key it falls back to the deterministic mock **loudly** — it never
silently fakes live intelligence.

`src/ceo_os/briefs.py` — self-contained worker brief builder (role + company
+ task + constraints + honest-limits footer). Includes briefs for the two new
hackathon workers: `ObjectionSimulator` (MKT) and `NegotiationCoach` (ACQ).

`src/ceo_os/demo.py` — end-to-end run: full CEO day, chairman brief in
Bengali, pending gates, provider health (calls, tokens).

## Run it

```bash
cd ceo-os
pip install -r requirements.txt
PYTHONPATH=src python3 -m ceo_os.demo                          # mock mode ($0, offline)
MODEL_API_KEY=LLM|... PYTHONPATH=src python3 -m ceo_os.demo    # live Muse Spark
python3 tests/test_meta_provider.py            # 6 tests, offline
```

The engine it drives lives in `~/workspace/boss-ceo` (v0.1, 13/13 workers
passing, on GitHub at `github.com/msredc5-bit/boss-ceo`). Set `BOSS_CEO_HOME`
if yours is elsewhere.

## 10-day build plan

- Days 1–2: `MetaProvider` live verification (latency, tokens per worker call)
- Days 3–5: prompt-engineer all 13 worker briefs against Muse Spark 1.3
- Days 6–7: wire `ObjectionSimulator` + `NegotiationCoach`
- Days 8–9: demo + cost/latency dashboard
- Day 10: docs + submission video

## Honest limits

- Token counts are tracked; **$ cost is not estimated** — Meta's price sheet rules.
- Mock mode is deterministic and labeled; live mode needs the hackathon's $150 credits.
- Gate words (`ok`, `send`, `post it`, …) belong to the founder — the system never says them.
