# Boss CEO — Md Mainuddin's Personal CEO Agent

Not the generic 50-division conglomerate. This is **Boss's own CEO**: 4 divisions
mirroring his real work, 15 workers running his actual SOPs, his approval gates
enforced **in code**, and the Chairman brief in **Bengali**.

## Quickstart

```bash
pip install -r requirements.txt   # pyyaml only
python3 scripts/boss_run.py       # one mock business day + Bengali chairman brief
```

$0 spend. Mock data only. Nothing leaves this machine.

## The org

| Division | Workers | What they do |
|---|---|---|
| **ACQ** Client Acquisition | ProspectResearcher, OutreachDrafter, ReplyHandler | His SDR team: find US home-service SMBs, draft outreach (draft-only), triage replies per the locked reply rule |
| **DEL** Receptionist Delivery | RetellBuilder, QAEngineer, OnboardingAgent | Build Ava-style Retell receptionists, run the QA checklist, draft onboarding packs |
| **MKT** Marketing & Content | ContentPlanner, VideoProducer, CaptionWriter, PublishPrep | Sunday 5-post plan, reel-factory video packages, caption packs, publish prep (never publishes) |
| **OPS** Operations & Admin | InboxTriager, ReportCompiler, SchedulerAssistant | Inbox drafts, visible-metrics-only weekly report, scheduling help |

## How it's customized

- `config/boss.yaml` — his profile: name, timezone (Asia/Dhaka), languages,
  Talvenor brand lock, gate words, standing rules. Edit the YAML, not the code.
- **Gates in code**: every worker declares `requires_gate` (`ok` / `post it` /
  `upload it` / `send` / `go`). The CEO collects them into "অপেক্ষমাণ অনুমোদন"
  (pending approvals) — nothing gated auto-advances.
- **Standing rules baked in**: no invented clients/prices/testimonials, no
  dental/medical targeting, email lane is draft-Elora/send-Boss, IG decline →
  polite exit / interest → draft only.
- **Bengali brief**: the chairman report renders in his language.

## Architecture

Same Layer 0–3 pattern as `ai-conglomerate` (contracts → mock → CEO →
templates), but every layer is Boss-shaped:

```
boss-ceo/
├── config/boss.yaml          # the customization: profile, gates, rules
├── src/contracts/            # Layer 0 interfaces (same as ai-conglomerate)
├── src/mock/                 # Layer 1 mock LLM ($0)
├── src/ceo/boss_ceo.py       # Layer 2: gate enforcement + Bengali brief
├── src/divisions/manager.py  # Layer 3 division template
├── src/workers/              # Layer 3: 13 custom workers (4 files by division)
├── src/store/                # SQLite (data/boss-ceo.db, gitignored)
└── scripts/boss_run.py       # the demo
```

## Going live (per worker, with approval)

Each worker is a shell today. To activate one: implement its `do_work` against
the real service (Retell API, Gmail, etc.), add the credential to `.env`
(gitignored), and get Boss's explicit approval for that exact worker.
