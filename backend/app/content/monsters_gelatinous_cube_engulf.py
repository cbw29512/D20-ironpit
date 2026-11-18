from __future__ import annotations

"""Foundation for 2014 Gelatinous Cube Engulf.

Printed 2014 Engulf:
The cube moves up to its speed. While doing so, it can enter Large or smaller
creatures' spaces. Whenever the cube enters a creature's space, the creature
must make a DC 12 Dexterity saving throw. On a failed save, the creature is
engulfed. The engulfed creature can't breathe, is restrained, and takes 6d6
acid damage at the start of each of the cube's turns. When the cube moves, the
engulfed creature moves with it. An engulfed creature can try to escape by
taking an action to make a DC 12 Strength check. On a success, the creature
escapes and enters a space of its choice within 5 feet of the cube.

Next wiring: bind the space-entry save, restrained/blinded state, and periodic
acid so it resolves in combat. Does not claim admission.
"""


def gelatinous_cube_engulf_notes() -> dict[str, object]:
    return {
        "monster": "Gelatinous Cube",
        "ability": "Engulf",
        "save": "DC 12 Dex",
        "effects": ["restrained", "can't breathe", "6d6 acid at start of cube's turn"],
        "escape": "DC 12 Strength check as an action",
    }
