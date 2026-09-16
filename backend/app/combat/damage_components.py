from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import DamageRollComponent, DamageType, DiceRoll

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, DamageType]


def roll_damage_component(
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


def fixed_damage_component(source: str, amount: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source=source,
        notation=str(amount),
        rolls=[],
        modifier=0,
        damage_type=damage_type,
        total=amount,
    )


def aggregate_damage_components(components: list[DamageRollComponent]) -> DiceRoll:
    return DiceRoll(
        notation=" + ".join(component.notation for component in components),
        rolls=[roll for component in components for roll in component.rolls],
        modifier=sum(component.modifier for component in components),
        total=sum(component.total for component in components),
    )
