"""Apply a previously resolved weapon hit against a breakable condition object.

Attack selection, range, Action economy and attack-vs-object AC belong to the
existing attack scheduler. This resolver only consumes the hit's rolled values.
"""
from __future__ import annotations

import logging
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.condition_immunity import condition_is_immune
from app.domain.models import CombatantState, TimedEffect, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def prefer_fresh_limited_breakable_control(
    attacker: CombatantState, target: CombatantState, attack: WeaponAttack,
) -> bool:
    """Spend a printed finite control attack on a target not already affected.

    This is universal policy for zero-damage ranged breakable restraints, not
    a source-name or creature-name resolver. Actual targeting and resource
    checks remain in the normal attack-choice and hit engines.
    """
    try:
        control = attack.control_effect
        if (
            attack.weapon.attack_kind is not WeaponAttackKind.RANGED
            or attack.resource_id is None or attack.fixed_damage != 0
            or attack.on_hit_damage or attack.on_hit_save_damage
            or attack.on_hit_condition_save or attack.conditional_damage
            or control is None or control.breakable_object is None
            or not control.condition_id
        ):
            return False
        return (
            control.condition_id not in target.active_effect_ids
            and not condition_is_immune(target, control.condition_id, attacker.template)
        )
    except Exception:
        logger.exception("Breakable-control attack policy failed for %s.", attack.id)
        raise


def damage_breakable_condition_object(
    target: CombatantState, effect: TimedEffect, attack_total: int,
    rolled_damage: int, damage_type: str,
) -> tuple[int, bool]:
    """Return (HP lost, destroyed); destroyed means the owning debuff ends."""
    try:
        if effect not in target.timed_effects or effect.breakable_object is None:
            raise ValueError("The target has no active breakable condition object.")
        if attack_total < 0 or rolled_damage < 0:
            raise ValueError("Resolved attack/damage values must be nonnegative.")
        obj = effect.breakable_object
        if attack_total < obj.armor_class:
            return 0, False
        if damage_type not in {part.value for part in obj.damage_immunities} | {
            part.value for part in obj.damage_vulnerabilities
        } and damage_type not in {
            "acid", "bludgeoning", "cold", "fire", "force", "lightning",
            "necrotic", "piercing", "poison", "psychic", "radiant",
            "slashing", "thunder",
        }:
            raise ValueError(f"Unknown breakable object damage type {damage_type!r}.")
        amount = 0 if damage_type in obj.damage_immunities else rolled_damage
        if amount and damage_type in obj.damage_vulnerabilities:
            amount *= 2
        applied = min(amount, obj.current_hp)
        obj.current_hp -= applied
        destroyed = obj.current_hp == 0
        if destroyed:
            remove_effect_group(target, effect)
        return applied, destroyed
    except Exception:
        logger.exception("Failed to damage breakable condition object on %s.", target.template.name)
        raise
