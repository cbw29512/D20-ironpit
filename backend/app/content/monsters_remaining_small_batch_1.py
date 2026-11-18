from __future__ import annotations

"""Foundation notes for 2014 remaining small blocker categories.

Remaining after prior foundation batches:
- attack:damage-type (2)
- source:reaction (2)
- arena:neutral (1)
- attack:none (1)
- arena:removed (1)

Targets for subsequent wiring (foundations only):
- attack:damage-type: Ettercap, Giant Spider
- source:reaction: Shield Guardian, Spectator
- arena:neutral: Frog
- attack:none: Rug of Smothering
- arena:removed: Stirge

No admission claims. Exact-head CI required.
"""


def remaining_small_batch_1_targets() -> dict[str, list[str]]:
    return {
        "attack:damage-type": ["Ettercap", "Giant Spider"],
        "source:reaction": ["Shield Guardian", "Spectator"],
        "arena:neutral": ["Frog"],
        "attack:none": ["Rug of Smothering"],
        "arena:removed": ["Stirge"],
    }
