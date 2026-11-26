from __future__ import annotations

"""Foundation for 2014 Darkmantle Darkness.

Printed 2014 Darkness (Recharge 6):
The darkmantle casts darkness on itself. Magical darkness spreads from a
point the darkmantle chooses within 15 feet of it. The darkness spreads
around corners. A creature with darkvision can't see through this darkness,
and nonmagical light can't illuminate it.

Next wiring: bind the darkness environment context so it resolves in combat.
Does not claim admission.
"""


def darkmantle_darkness_notes() -> dict[str, object]:
    return {
        "monster": "Darkmantle",
        "ability": "Darkness",
        "recharge": "6",
        "effect": "magical darkness on self, 15-ft range, blocks darkvision",
    }
