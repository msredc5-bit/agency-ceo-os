"""Self-contained worker briefs — the founder-skill pattern.

A worker brief must stand alone: role + company profile + task + constraints +
honest-limits footer. No hidden conversation state, so any model (mock today,
Muse Spark tomorrow) can serve any worker.
"""
from __future__ import annotations


HONEST_LIMITS_FOOTER = """
HONEST LIMITS (always obey):
- Never invent clients, testimonials, prices, statistics, or results.
- If a number is needed and not provided, name the missing input — do not guess.
- Mark every claim VERIFIED (from the brief) or ASSUMPTION (your inference).
- If the task needs a human decision, end with: GATE: <gate-word> — <what you need>.
"""


def build_brief(
    *,
    worker_role: str,
    division: str,
    company: str,
    task: str,
    constraints: str = "",
    context: str = "",
) -> str:
    parts = [
        f"ROLE: {worker_role} — {division} division, {company}.",
        f"TASK: {task}",
    ]
    if context:
        parts.append(f"CONTEXT:\n{context}")
    if constraints:
        parts.append(f"CONSTRAINTS:\n{constraints}")
    parts.append(HONEST_LIMITS_FOOTER.strip())
    parts.append("FORMAT: short, concrete, bullet points. No fluff.")
    return "\n\n".join(parts)


# Two new workers the mock provider couldn't support — planned for hackathon days 6-7.
NEW_WORKERS = {
    "ObjectionSimulator": {
        "division": "MKT",
        "role": "Simulates prospect pushback before real outreach goes out",
        "task": ("Given an outreach draft and a prospect profile, play the skeptical "
                 "prospect. List the 5 most likely objections in the prospect's own words, "
                 "ranked by likelihood, each with a one-line rebuttal angle. Be harsh — "
                 "a weak draft must not survive this review."),
    },
    "NegotiationCoach": {
        "division": "ACQ",
        "role": "Prepares the founder for the live sales call",
        "task": ("Given the prospect profile and call goal, produce: 3 likely questions "
                 "with strong answers, 2 traps to avoid, and a 60-second opening script "
                 "in plain US English. Flag anything that needs the founder's decision "
                 "as GATE."),
    },
}
