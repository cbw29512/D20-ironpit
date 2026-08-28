from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import (
    CombatantState,
    DamageRollComponent,
    RollMode,
    WeaponAttack,
    WeaponAttackKind,
    WeaponProperty,
)

logger = logging.getLogger(__name__)
SNEAK_ATTACK = "sneak-attack"


def can_sneak_attack(
    attacker: CombatantState,
    attack: WeaponAttack,
    attack_mode: RollMode,
) -> bool:
    try:
        weapon = attack.weapon
        eligible_weapon = (
            WeaponProperty.FINESSE in weapon.properties
            or weapon.attack_kind is WeaponAttackKind.RANGED
        )
        return bool(
            attacker.template.sneak_attack_dice_count > 0
            and SNEAK_ATTACK not in attacker.once_per_turn_features_used
            and eligible_weapon
            and attack_mode is RollMode.ADVANTAGE
        )
    except Exception as exc:
        logger.exception("Sneak Attack eligibility failed for %s.", attacker.template.name)
        raise RuntimeError("Sneak Attack eligibility could not be resolved.") from exc


def resolve_sneak_attack_component(
    attacker: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    attack_mode: RollMode,
) -> DamageRollComponent | None:
    try:
        if not can_sneak_attack(attacker, attack, attack_mode):
            return None

        count = attacker.template.sneak_attack_dice_count * (2 if critical else 1)
        rolls = [dice.roll(6) for _ in range(count)]
        attacker.once_per_turn_features_used.add(SNEAK_ATTACK)
        return DamageRollComponent(
            source="Sneak Attack",
            notation=f"{count}d6+0",
            rolls=rolls,
            modifier=0,
            damage_type=attack.weapon.damage_type,
            total=sum(rolls),
        )
    except Exception as exc:
        logger.exception("Sneak Attack resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Sneak Attack could not be resolved.") from exc
