"""Strict 2014 source binding: owner-linked grapple damage, not an extra attack."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.actions import GrapplePeriodicDamage

logger = logging.getLogger(__name__)
_KEYS = frozenset({
    "id", "name", "dice_count", "dice_size", "damage_bonus",
    "damage_type", "apply_on", "ends_when_grapple_source_ends",
})


def supports_grapple_periodic_2014(attack: SourceAttack2014) -> bool:
    """Only accept a complete on-hit, grapple-owner-lifetime damage declaration."""
    value = attack.ongoing_damage_effect
    control = attack.control_effect
    if not isinstance(value, dict) or set(value) != _KEYS or not isinstance(control, dict):
        return False
    return (
        isinstance(value["id"], str) and bool(value["id"])
        and isinstance(value["name"], str) and bool(value["name"])
        and isinstance(value["dice_count"], int) and 1 <= value["dice_count"] <= 40
        and isinstance(value["dice_size"], int) and 2 <= value["dice_size"] <= 100
        and value["damage_bonus"] == 0
        and value["damage_type"] in {"acid", "bludgeoning", "cold", "fire", "force",
            "lightning", "necrotic", "piercing", "poison", "psychic", "radiant",
            "slashing", "thunder"}
        and value["apply_on"] == "hit"
        and value["ends_when_grapple_source_ends"] is True
        and isinstance(control.get("grapple_escape_dc"), int)
        and control["grapple_escape_dc"] >= 1
        and control.get("restrains_while_grappled") is True
        and attack.forbid_target_grappled_by_self is True
    )


def grapple_periodic_damage_2014(attack: SourceAttack2014) -> GrapplePeriodicDamage:
    try:
        if not supports_grapple_periodic_2014(attack):
            raise ValueError(f"Unsupported 2014 grapple periodic rider on {attack.id}.")
        value = attack.ongoing_damage_effect
        return GrapplePeriodicDamage(
            source_name=value["name"],
            dice_count=value["dice_count"], dice_size=value["dice_size"],
            damage_type=value["damage_type"],
        )
    except Exception:
        logger.exception("Grapple-source periodic damage binding failed for %s.", attack.id)
        raise


def source_grapple_periodic_proof_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> bool:
    """For the Chain source, confirm the printed rider remains pinned and legible."""
    if monster.id != "chain-devil" or attack.id != "chain":
        return True
    source = monster.source_actions or ""
    expected = (
        "escape DC 14", "takes 7 (2d6) piercing damage",
        "start of each of its turns", "if the devil isn't already grappling",
    )
    value = attack.ongoing_damage_effect
    if (not supports_grapple_periodic_2014(attack)
        or not all(s in source for s in expected)
        or (attack.attack_bonus, attack.reach_ft, attack.damage.dice_count,
            attack.damage.dice_size, attack.damage.bonus, attack.damage.type)
            != (8, 10, 2, 6, 4, "slashing")
        or attack.control_effect["grapple_escape_dc"] != 14
        or (value["dice_count"], value["dice_size"], value["damage_type"]) != (2, 6, "piercing")):
        raise ValueError("2014 Chain periodic damage disagrees with pinned source.")
    return True
