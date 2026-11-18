from __future__ import annotations

"""Foundation for 2014 Roper Reel.

Printed 2014 Reel:
The roper pulls each creature grappled by it up to 25 feet straight toward it.

Next wiring: bind the forced pull so it resolves in combat (subject to the
locked #1032 forced-movement policy). Does not claim admission.
"""


def roper_reel_notes() -> dict[str, object]:
    return {
        "monster": "Roper",
        "ability": "Reel",
        "cost": "action",
        "effect": "pull each grappled creature up to 25 feet toward the roper",
        "note": "forced movement subject to locked #1032 arena rule",
    }
