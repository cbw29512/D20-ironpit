from __future__ import annotations

import logging

from app.combat.barbarian import rage_damage_bonus
from app.combat.brutal_critical import brutal_critical_bonus_damage
from app.combat.conditional_damage import active_replacement_damage, conditional_damage_active
from app.combat.dice import DiceProvider
from app.combat.frenzy import frenzy_bonus_damage
from app.combat.savage_attacker import roll_weapon_component
from app.combat.sneak_attack import sneak_attack_bonus_damage
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll, RollMode, WeaponAttack

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, DamageType]


def roll_damage_component(
    dice: DiceProvider, source: str, dice_count: int, dice_size: int, modifier: int,
    damage_type: DamageType, critical: bool,
) -> DamageRollComponent:
    try:
        count = dice_count * (2 if critical else 1)
        rolls = [dice.roll(dice_size) for _ in range(count)]
        return DamageRollComponent(
            source=source, notation=f"{count}d{dice_size}+{modifier}", rolls=rolls,
            modifier=modifier, damage_type=damage_type, total=sum(rolls) + modifier,
        )
    except Exception as exc:
        logger.exception("Failed to roll damage component %s.", source)
        raise RuntimeError("Damage component could not be resolved.") from exc


def fixed_damage_component(source: str, amount: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source=source, notation=str(amount), rolls=[], modifier=0, damage_type=damage_type, total=amount,
    )


def aggregate_damage_components(components: list[DamageRollComponent]) -> DiceRoll:
    return DiceRoll(
        notation=" + ".join(component.notation for component in components),
        rolls=[roll for component in components for roll in component.rolls],
        modifier=sum(component.modifier for component in components),
        total=sum(component.total for component in components),
    )


def _append_bonus_component(
    components: list[DamageRollComponent], dice: DiceProvider,
    spec: BonusDamageSpec | None, *, critical: bool,
) -> None:
    if spec is None:
        return
    source, dice_count, dice_size, damage_type = spec
    components.append(roll_damage_component(
        dice, source, dice_count, dice_size, 0, damage_type, critical,
    ))


def resolve_weapon_damage(
    attacker: CombatantState, attack: WeaponAttack, dice: DiceProvider, critical: bool,
    attack_mode: RollMode, turn_key: str | None = None,
    bonus_damage: BonusDamageSpec | None = None, target: CombatantState | None = None,
    sneak_attack_ally_available: bool = False,
) -> tuple[DiceRoll, list[DamageRollComponent]]:
    """Resolve weapon dice or fixed damage plus certified hit-specific riders."""
    try:
        weapon = attack.weapon
        replacement = active_replacement_damage(attacker, target, attack, attack_mode)
        if replacement is not None:
            components = [roll_damage_component(
                dice, weapon.name, replacement.dice_count, replacement.dice_size,
                replacement.damage_bonus, replacement.damage_type, critical,
            )]
        elif attack.fixed_damage is not None:
            components = [fixed_damage_component(weapon.name, attack.fixed_damage, weapon.damage_type)]
        else:
            weapon_modifier = attack.damage_bonus + rage_damage_bonus(attacker, attack)
            components = [roll_weapon_component(
                attacker, dice, source=weapon.name, dice_count=weapon.dice_count,
                dice_size=weapon.dice_size, modifier=weapon_modifier, damage_type=weapon.damage_type,
                critical=critical, turn_key=turn_key, damage_die_minimum=attack.damage_die_minimum,
            )]

        _append_bonus_component(
            components, dice, brutal_critical_bonus_damage(attacker, attack, critical), critical=False,
        )
        for extra in attack.on_hit_damage:
            if extra.dice_count == 0:
                components.append(fixed_damage_component(extra.source, extra.damage_bonus, extra.damage_type))
            else:
                components.append(roll_damage_component(
                    dice, extra.source, extra.dice_count, extra.dice_size,
                    extra.damage_bonus, extra.damage_type, critical,
                ))

        for conditional in attack.conditional_damage:
            if conditional.mode != "add" or not conditional_damage_active(conditional, attacker, target, attack_mode):
                continue
            source = "Advantage bonus damage" if conditional.trigger == "attack_advantage" else "Conditional bonus damage"
            components.append(roll_damage_component(
                dice, source, conditional.dice_count, conditional.dice_size,
                conditional.damage_bonus, conditional.damage_type, critical,
            ))

        _append_bonus_component(
            components, dice,
            sneak_attack_bonus_damage(attacker, attack, attack_mode, turn_key, sneak_attack_ally_available),
            critical=critical,
        )
        _append_bonus_component(components, dice, frenzy_bonus_damage(attacker, attack, turn_key), critical=critical)
        _append_bonus_component(components, dice, bonus_damage, critical=critical)
        return aggregate_damage_components(components), components
    except Exception as exc:
        logger.exception("Weapon damage resolution failed for %s.", attacker.template.name)
        raise RuntimeError("Weapon damage could not be resolved.") from exc
