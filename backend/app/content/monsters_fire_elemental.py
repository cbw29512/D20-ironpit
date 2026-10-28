from __future__ import annotations

"""Foundation for 2014 Fire Elemental Fire Form.

Printed 2014 Fire Form:
- Move through 1-inch spaces without squeezing
- Touch or melee hit within 5 ft deals 1d10 fire
- Can enter hostile space; first entry on a turn deals 1d10 fire and ignites

Next wiring: bind the contact and space-entry damage to existing
MeleeHitRetaliation / TimedEmanationDamage primitives so it resolves
in combat. Does not claim admission.
"""


def fire_elemental_fire_form_notes() -> dict[str, object]:
    return {
        "monster": "Fire Elemental",
        "trait": "Fire Form",
        "contact_damage": "1d10 fire within 5 ft",
        "space_entry_damage": "1d10 fire on first entry per turn",
        "ignite": "ongoing 1d10 fire until doused",
    }
