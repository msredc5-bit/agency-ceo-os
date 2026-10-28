# Security notes — Agency CEO OS

- **Keys never live in this repo.** `MODEL_API_KEY` (Meta Model API) comes
  from the environment only. See `ceo-os/.env.example` for the placeholder.
  If you fork or connect this repo to another agent, use YOUR OWN key and
  YOUR OWN business config (`boss-ceo/config/boss.yaml`) — you get your own
  copy of the system, not access to anyone else's business.
- **Gates are the safety system.** Send / publish / spend / delete never
  auto-advance; they wait for the owner's exact word (`ok`, `post it`,
  `upload it`, `send`, `go`).
- **Workers do not execute real external actions by themselves.** They draft
  and plan through the model. Real sends, bookings, or API calls need an
  explicit execution step outside this code.
- **Before every push, run the secret scan:**
  `python3 boss-ceo/scripts/scan_secrets.py` — it fails on key-like values
  and allows placeholders and test keys.
- **No license file is included yet.** Until the owner adds one, do not
  assume this code is free to reuse commercially.
