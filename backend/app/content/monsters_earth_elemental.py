from __future__ import annotations

"""Foundation for 2014 Earth Elemental Earth Glide and Siege Monster.

Printed 2014:
- Earth Glide: can burrow through nonmagical, unworked earth and stone;
  does not disturb the material it moves through.
- Siege Monster: double damage to objects and structures.

Next wiring: bind the burrow permission and siege damage multiplier to
existing movement and damage primitives so it resolves in combat.
Does not claim admission.
"""


def earth_elemental_notes() -> dict[str, object]:
    return {
        "monster": "Earth Elemental",
        "traits": ["Earth Glide", "Siege Monster"],
        "earth_glide": "burrow through nonmagical unworked earth and stone",
        "siege": "double damage to objects and structures",
    }
