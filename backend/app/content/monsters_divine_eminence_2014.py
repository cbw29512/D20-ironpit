from __future__ import annotations

"""Foundation for 2014 Priest Divine Eminence.

Printed 2014 Divine Eminence:
As a bonus action, the priest can expend a spell slot to cause its melee weapon
attacks to magically deal an extra 10 (3d6) radiant damage to a target on a hit.
This benefit lasts until the end of the turn. If the priest expends a spell slot
of 2nd level or higher, the extra damage increases by 1d6 for each level above 1st.

Shared semantic: bonus action + limited spell-slot resource → timed (end of turn)
on-hit extra typed radiant damage rider, scaling with expended slot level.
No name dispatch. Next: bind to existing universal resource, bonus-action, timed
modifier and on-hit damage primitives with Python/browser parity and tests.
Does not claim admission or clear source:trait / mechanic:spellcasting blockers.
"""


def divine_eminence_notes() -> dict[str, object]:
    return {
        "monster": "Priest",
        "trait": "Divine Eminence",
        "effect": "bonus action expend spell slot for end-of-turn on-hit 3d6+ radiant damage",
        "status": "foundation",
    }
