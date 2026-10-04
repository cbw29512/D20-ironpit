from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction, SpellModifierEffect
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"
_ALL_DAMAGE = [item.value for item in DamageType]
_ENERGY = ["acid", "cold", "fire", "lightning", "thunder"]


def warding_bond_2014() -> DefensiveSpellAction:
    """Build 2014 Warding Bond: +1 AC/saves, all-type resistance, shared damage within 60 feet."""
    try:
        return DefensiveSpellAction(
            id="warding-bond",
            name="Warding Bond",
            level=2,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            damage_resistances=_ALL_DAMAGE,
            share_damage_with_source=True,
            share_range_ft=60,
            concentration=False,
            priority=70,
            modifier_effects=[
                SpellModifierEffect(kind="armor-class", flat_bonus=1),
                SpellModifierEffect(kind="saving-throw-flat", flat_bonus=1),
            ],
            animation="warding-bond",
            source=f"{_SOURCE}: Warding Bond",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Warding Bond.")
        raise


def protection_from_energy_2014() -> DefensiveSpellAction:
    """Build 2014 Protection from Energy as a chosen acid/cold/fire/lightning/thunder resistance."""
    try:
        return DefensiveSpellAction(
            id="protection-from-energy",
            name="Protection from Energy",
            level=3,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            selectable_resistance_types=_ENERGY,
            concentration=True,
            priority=75,
            animation="protection-from-energy",
            source=f"{_SOURCE}: Protection from Energy",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Protection from Energy.")
        raise


def magic_weapon_2014() -> DefensiveSpellAction:
    """Build 2014 Magic Weapon as +1 attack and +1 weapon damage on the touched wielder."""
    try:
        return DefensiveSpellAction(
            id="magic-weapon",
            name="Magic Weapon",
            level=2,
            action_cost="bonus_action",
            range_ft=5,
            duration_minutes=60,
            target_policy="self",
            target_count=1,
            concentration=True,
            priority=55,
            modifier_effects=[
                SpellModifierEffect(kind="attack-roll-flat", flat_bonus=1),
                SpellModifierEffect(kind="weapon-damage-flat", flat_bonus=1),
            ],
            animation="magic-weapon",
            source=f"{_SOURCE}: Magic Weapon",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Magic Weapon.")
        raise
