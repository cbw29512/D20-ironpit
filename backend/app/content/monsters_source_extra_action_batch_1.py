from __future__ import annotations

"""Foundation notes for 2014 source:extra-action batch 1.

Highest-yield remaining category not already covered by an open PR
(source:trait has #1083; recharge families have dedicated drafts).

Targets for subsequent wiring (reuse existing universal primitives only):
- Representative pure or lightly-overlapped extra Actions not in Swallow/recharge/spell PRs
- e.g. Darkmantle Darkness, Otyugh Tentacle, Gelatinous Cube Engulf (if not covered), Roper Reel, etc.

No name dispatch. Source-verify each. Python/browser parity required.
No admission claims. Exact-head CI required before any blocker clearance.
"""


def source_extra_action_batch_1_targets() -> list[str]:
    return [
        "Darkmantle Darkness",
        "Otyugh Tentacle",
        "Roper Reel",
        "Gelatinous Cube Engulf",
        "Cloaker Phantasms",
    ]
