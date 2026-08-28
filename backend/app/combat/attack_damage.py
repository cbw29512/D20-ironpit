from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.barbarian import rage_damage_component
from app.combat.damage import resolve_weapon_damage
from app.combat.damage_taken import resolve_damage_taken
from app.combat.dice import DiceProvider
from app.combat.rogue import resolve_sneak_attack_component
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll, RollMode, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass
class AttackDamageResolution:
    roll: DiceRoll
    components: list[DamageRollComponent]
    applied: int
    sneak_attack_applied: bool
    resisted: set[DamageType]
    immune: set[DamageType]
    vulnerable: set[DamageType]


def resolve_attack_damage(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    mode: RollMode,
    include_positive_ability_modifier: bool,
) -> AttackDamageResolution:
    try:
        roll, components = resolve_weapon_damage(
            attacker,
            attack,
            dice,
            critical,
            mode,
            include_positive_ability_modifier,
        )
        sneak = resolve_sneak_attack_component(attacker, attack, dice, critical, mode)
        if sneak is not None:
            components.append(sneak)
            roll.notation += f" + {sneak.notation}"
            roll.rolls.extend(sneak.rolls)
            roll.total += sneak.total

        rage = rage_damage_component(attacker, attack)
        if rage is not None:
            components.append(rage)
            roll.notation += f" + {rage.notation}"
            roll.modifier += rage.modifier
            roll.total += rage.total

        applied, resisted, immune, vulnerable = resolve_damage_taken(defender, components)
        defender.current_hp = max(0, defender.current_hp - applied)
        defender.is_alive = defender.current_hp > 0
        return AttackDamageResolution(
            roll=roll,
            components=components,
            applied=applied,
            sneak_attack_applied=sneak is not None,
            resisted=resisted,
            immune=immune,
            vulnerable=vulnerable,
        )
    except Exception as exc:
        logger.exception("Attack damage failed: %s -> %s.", attacker.template.name, defender.template.name)
        raise RuntimeError("Attack damage could not be resolved.") from exc
