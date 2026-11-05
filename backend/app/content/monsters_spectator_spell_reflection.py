from __future__ import annotations

"""Foundation for 2014 Spectator Spell Reflection.

Printed 2014 Spell Reflection:
If the spectator makes a successful saving throw against a spell, or a spell
attack misses it, the spectator can choose to magically reflect the spell
back at the caster as a reaction, forcing the caster to make a saving throw
or be hit by the attack.

Next wiring: bind the reaction reflection so it resolves in combat.
Does not claim admission.
"""


def spectator_spell_reflection_notes() -> dict[str, object]:
    return {
        "monster": "Spectator",
        "ability": "Spell Reflection",
        "cost": "reaction",
        "trigger": "successful save vs spell or spell attack miss",
        "effect": "reflect the spell back at the caster",
    }
