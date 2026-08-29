from __future__ import annotations

import logging

from app.combat.barbarian import rage_damage_bonus
from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll, RollMode, WeaponAttack

logger = logging.getLogger(__name__)


def _roll_component(
    dice: DiceProvider,
    source: str,
    dice_count: int,
    dice_size: int,
    modifier: int,
    damage_type: DamageType,
    critical: bool,
) -> DamageRollComponent:
    try:
        count = dice_count * (2 if critical else 1)
        rolls = [dice.roll(dice_size) for _ in range(count)]
        return DamageRollComponent(
            source=source,
            notation=f"{count}d{dice_size}+{modifier}",
            rolls=rolls,
            modifier=modifier,
            damage_type=damage_type,
            total=sum(rolls) + modifier,
        )
    except Exception as exc:
        logger.exception("Failed to roll damage component %s.", source)
        raise RuntimeError("Damage component could not be resolved.") from exc


def resolve_weapon_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    attack_mode: RollMode,
) -> tuple[DiceRoll, list[DamageRollComponent]]:
    """Resolve intrinsic weapon dice plus combatant-specific modifiers and riders."""
    try:
        weapon = attack.weapon
        weapon_modifier = attack.damage_bonus + rage_damage_bonus(attacker, attack)
        components = [
            _roll_component(
                dice=dice,
                source=weapon.name,
                dice_count=weapon.dice_count,
                dice_size=weapon.dice_size,
                modifier=weapon_modifier,
                damage_type=weapon.damage_type,
                critical=critical,
            )
        ]

        for conditional in attack.conditional_damage:
            if conditional.trigger == "attack_advantage" and attack_mode is RollMode.ADVANTAGE:
                components.append(
                    _roll_component(
                        dice=dice,
                        source="Advantage bonus damage",
                        dice_count=conditional.dice_count,
                        dice_size=conditional.dice_size,
                        modifier=conditional.damage_bonus,
                        damage_type=conditional.damage_type,
                        critical=critical,
                    )
                )

        aggregate_rolls = [roll for component in components for roll in component.rolls]
        aggregate_total = sum(component.total for component in components)
        notation = " + ".join(component.notation for component in components)
        return (
            DiceRoll(
                notation=notation,
                rolls=aggregate_rolls,
                modifier=sum(component.modifier for component in components),
                total=aggregate_total,
            ),
            components,
        )
    except Exception as exc:
        logger.exception("Weapon damage resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Weapon damage could not be resolved.") from exc
