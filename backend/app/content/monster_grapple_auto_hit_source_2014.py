"""Source-prove an existing grapple making future weapon hits automatic.

The source labels identify printed text only; the combat engine sees a generic
targeting/hit policy and the active owner-linked grapple state.
"""
from __future__ import annotations

from app.content.monster_source_sections_2014 import source_sections_2014


def source_proves_grapple_auto_hit_2014(monster, attack) -> bool:
    if attack.grapple_target_policy != "auto_hit_own_grapple":
        return False
    if attack.kind != "melee" or not isinstance(attack.control_effect, dict):
        return False
    if not (attack.control_effect.get("grapple_escape_dc")
            and attack.control_effect.get("restrains_while_grappled")):
        return False
    clause = source_sections_2014(monster.source_actions).get(attack.name, "").casefold()
    label = attack.name.casefold()
    return (
        f"automatically hit the target with its {label}" in clause
        and f"can't make {label} attacks against other targets" in clause
    )
