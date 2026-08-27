from __future__ import annotations

import logging

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


def calculate_applied_damage(
    defender: CombatantState,
    components: list[DamageRollComponent],
) -> int:
    """Group damage by type, then apply Immunity and SRD Resistance/Vulnerability order."""
    try:
        totals_by_type: dict[DamageType, int] = {}
        for component in components:
            totals_by_type[component.damage_type] = totals_by_type.get(component.damage_type, 0) + component.total

        total = 0
        template = defender.template
        for damage_type, raw_damage in totals_by_type.items():
            if damage_type in template.damage_immunities:
                continue

            applied = raw_damage
            if damage_type in template.damage_resistances:
                applied //= 2
            if damage_type in template.damage_vulnerabilities:
                applied *= 2
            total += max(0, applied)
        return total
    except Exception as exc:
        logger.exception("Damage defense resolution failed for %s.", defender.template.name)
        raise RuntimeError("Applied damage could not be resolved.") from exc


def _rider_applies(trigger: str, attack_mode: RollMode) -> bool:
    return trigger == "always" or (
        trigger == "attack_advantage" and attack_mode is RollMode.ADVANTAGE
    )


def resolve_weapon_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    attack_mode: RollMode,
) -> tuple[DiceRoll, list[DamageRollComponent]]:
    """Resolve an attack profile without mutating intrinsic equipment dice."""
    try:
        weapon = attack.weapon
        base_dice_count = attack.damage_dice.dice_count if attack.damage_dice else weapon.dice_count
        base_dice_size = attack.damage_dice.dice_size if attack.damage_dice else weapon.dice_size
        components = [
            _roll_component(
                dice=dice,
                source=weapon.name,
                dice_count=base_dice_count,
                dice_size=base_dice_size,
                modifier=attack.damage_bonus,
                damage_type=weapon.damage_type,
                critical=critical,
            )
        ]

        for rider in attack.conditional_damage:
            if not _rider_applies(rider.trigger, attack_mode):
                continue
            source = "Advantage bonus damage" if rider.trigger == "attack_advantage" else "Bonus damage"
            components.append(
                _roll_component(
                    dice=dice,
                    source=source,
                    dice_count=rider.dice_count,
                    dice_size=rider.dice_size,
                    modifier=rider.damage_bonus,
                    damage_type=rider.damage_type,
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
