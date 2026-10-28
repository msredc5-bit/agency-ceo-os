# Deploy notes — Agency CEO OS

## What "complete setup" means here (honest scope)

Complete: org (CEO + 4 divisions + 15 workers), gates in code, mock demo,
live-provider wiring (Meta Model API, Muse Spark), provider tests, demo
dashboard page, this deploy guide.
NOT complete by code alone: a live API key, a 24/7 server, real tool
credentials (email / calendar / Vapi / Retell). Those need Boss's decisions
and accounts — no code can invent them.

## Run it anywhere (a computer that stays on)

```bash
python3 -m pip install -r boss-ceo/requirements.txt  # pyyaml only
python3 boss-ceo/scripts/boss_run.py                 # mock, $0
cd ceo-os && PYTHONPATH=src python3 -m ceo_os.demo  # mock, or live with key
```

## Go live (when Boss says so, in this order)

1. Credits confirmed in Meta Billing + a card on file (card gets a temporary
   pre-authorisation hold; Spend Limit is an alert, NOT a hard cap).
2. Create `MODEL_API_KEY` at dev.meta.ai. Never commit it. Pass it only via
   environment or the secure route — never in chat, never in a file.
3. Run one tiny call only: `MODEL_API_KEY=... PYTHONPATH=src python3 scripts/live_check.py`
   Check the printed token counts before any bigger run.
4. Then run the full demo: `MODEL_API_KEY=... PYTHONPATH=src python3 -m ceo_os.demo`

## 24/7 hosting (later, Boss's choice)

Any small Linux server works: install Python, copy this repo, set the key in
the environment, run the demo on a schedule or on demand. No hosting is
bought or configured in this repo. GitHub here is storage + review, not the
place the code runs — the server is where it runs.

## COO decision (2026-10-29)

No COO layer. The Main CEO + 4 Division Managers already coordinate 15
workers; a COO would duplicate the division managers. Revisit only when the
business count grows past one agency.
