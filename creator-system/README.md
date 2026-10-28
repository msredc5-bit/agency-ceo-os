# Creator Studio — Content Creation, Media & Entertainment

The second system next to Talvenor, from the 136-business map
(domain: Content Creation, Media & Entertainment — divisions D21–D30 are
the map's shell; this is the first one actually built).

For content creators, any format: short video, long video, carousel,
image, blog, podcast script. One idea, adapted per platform.

## Flow (Boss's order)

1. **CEO decision** — go or not, in one line.
2. **Topic research** — what to make, angle, audience.
3. **Script** — hook in first 2 seconds, one idea, simple CTA.
4. **Visual plan** — shot list, thumbnail idea, on-screen text.
5. **Caption pack** — hook first line, hashtags per platform.
6. **Publish prep — GATE** — prepared only. Nothing publishes until the
   owner says `post it` (video: `upload it`).
7. **Performance report** — template only; never estimated numbers, only
   platform numbers the owner pastes.

## Workers (6)

TopicResearcher, ScriptWriter, VisualProducer, CaptionWriter,
PublishPrep, PerformanceTracker — all on the boss-ceo engine
(`WorkerBase`), so a failing worker cannot crash the run, and every
gated output waits for the owner's exact word.

## Run (mock, $0)

```bash
python3 scripts/creator_run.py --niche "cooking" --format "short video"
python3 scripts/creator_run.py --niche "cooking" --report-json out.json
python3 tests/test_creator.py
```

## Honest labels

- Mock only: workers plan and draft through the model. No real video
  rendering, no publishing, no sending, no spend.
- No invented stats, clients, results, or quotes. No copyrighted music,
  characters, or copied work. No real person's face/voice imitation.
- Live mode (Muse Spark via API key) is the same wiring as ceo-os:
  swap the mock provider when a key exists — never commit a key.
