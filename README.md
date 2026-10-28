# Agency CEO OS — private review copy

One Main CEO Bot running an AI agency system, powered by Meta's Muse Spark
models. This is Boss's personal agency system (Talvenor), kept here for his
review before any public release.

## What is inside

- `boss-ceo/` — the agency system itself: 4 divisions (acquisition, delivery,
  marketing, operations), 15 workers, approval gates in code. Nothing gated
  (send / publish / spend / delete) auto-advances without Boss's word.
- `ceo-os/` — the hackathon demo engine: Meta API provider (live Muse Spark
  when `MODEL_API_KEY` is set, loud mock fallback otherwise), demo runner,
  one-tiny-call live check, provider tests (6/6).

## Status (honest)

- Mock-tested, $0 spent. Live mode needs a `MODEL_API_KEY` (never committed
  here — keys come from the environment only; see `ceo-os/.env.example`).
- The 136-business / 1,189-worker conglomerate is the larger plan, not what
  is wired here. What runs here is one business: Talvenor. Other businesses
  start only after this one works correctly.
- No real client data, no prices quoted in code, no invented testimonials.

## Run (mock, $0)

```bash
pip install -r boss-ceo/requirements.txt   # pyyaml only
python3 boss-ceo/scripts/boss_run.py
```

## Completion update — 2026-10-29 (verified)

- **COO: NOT added, on purpose.** The Main CEO + 4 Division Managers already
  coordinate 15 workers; a COO would duplicate the division managers. Revisit
  only when the business count grows past one agency.
- **Rosters synced to 15 workers** everywhere (`boss_run.py` was still on 13).
- **Added:** `dashboard.html` (demo dashboard, honestly labelled mock) and
  `DEPLOY.md` (how to run anywhere, how to go live, what still needs Boss).
- **Verified this day:** mock boss run (16 calls, $0), mock demo run (9 pending
  gates, none auto-advanced), provider tests 6/6, live-check correctly SKIP
  without a key ($0 spent).
- **Still needs Boss (no code can invent these):** API key for the live test,
  and a hosting choice if it must run 24/7. Until then: mock only, $0.
