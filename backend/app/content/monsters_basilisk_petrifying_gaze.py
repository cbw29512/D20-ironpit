from __future__ import annotations

"""Foundation for 2014 Basilisk Petrifying Gaze.

Printed 2014 Petrifying Gaze:
If a creature starts its turn within 30 feet of the basilisk and the two of
them can see each other, the basilisk can force the creature to make a DC 12
Constitution saving throw if the basilisk isn't incapacitated. On a failed
save, the creature magically begins to turn to stone and is restrained. It
must repeat the saving throw at the end of its next turn. On a success, the
effect ends. On a failure, the creature is petrified until freed by the
greater restoration spell or other magic.

Next wiring: bind the start-of-turn gaze save and progressive petrification
so it resolves in combat. Does not claim admission.
"""


def basilisk_petrifying_gaze_notes() -> dict[str, object]:
    return {
        "monster": "Basilisk",
        "ability": "Petrifying Gaze",
        "trigger": "creature starts turn within 30 ft and both can see each other",
        "save": "DC 12 Con",
        "effects": ["restrained on first fail", "petrified on second fail"],
    }
