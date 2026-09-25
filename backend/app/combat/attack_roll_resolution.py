from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.attack_advantage_suppression import apply_defender_advantage_suppression
from app.combat.barbarian import extend_rage_from_attack
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.brutal_strike import brutal_strike_attack_sources
from app.combat.conditions import attack_roll_condition_sources
from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.d20_bonus_dice import apply_d20_bonus_die_if_useful
from app.combat.dice import DiceProvider
from app.combat.heroic_inspiration import reroll_failed_attack_with_heroic_inspiration
from app.combat.modifier_stack import (
    apply_d20_bonus_dice,
    attack_roll_flat_bonus,
    attacks_against_advantage_sources,
    consume_attacks_against_advantage,
    consume_next_attack_against_advantage,
    effective_armor_class,
    next_attack_against_advantage_sources,
)
from app.combat.range import resolve_attack_roll_mode
from app.combat.reckless_attack import attacks_against_reckless_advantage, reckless_attack_advantage
from app.combat.rolls import roll_d20
from app.combat.sap import consume_sap, sap_disadvantage
from app.domain.models import CombatantState, DiceRoll, RollMode, WeaponAttack
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttackRollResolution:
    roll: DiceRoll
    mode: RollMode
    heroic_reroll: bool
    brutal_strike_disadvantage: int
    d20_bonus_source_name: str | None = None


def resolve_attack_roll(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    *,
    defender_event_id: str,
    round_number: int,
    turn_key: str | None,
    advantage_sources: int,
    other_disadvantage_sources: int,
    close_enemy_active: bool,
) -> AttackRollResolution:
    """Resolve the shared attack-roll source stack and consume roll-scoped modifiers."""
    try:
        condition_advantage, condition_disadvantage = attack_roll_condition_sources(
            attacker, defender, distance_ft, defender_event_id,
        )
        disadvantage_total = (
            other_disadvantage_sources + condition_disadvantage + sap_disadvantage(attacker)
        )
        reckless_advantage = reckless_attack_advantage(attacker, attack)
        reckless_advantage, brutal_disadvantage = brutal_strike_attack_sources(
            attacker,
            attack,
            turn_key,
            reckless_advantage=reckless_advantage,
            disadvantage_sources=disadvantage_total,
        )
        attack_advantage = apply_defender_advantage_suppression(
            defender,
            advantage_sources
            + condition_advantage
            + bloodied_fury_advantage(attacker, attack)
            + attacks_against_advantage_sources(defender)
            + attacks_against_reckless_advantage(defender)
            + reckless_advantage
            + conditional_attack_advantage_sources(attack, defender)
            + next_attack_against_advantage_sources(attacker, defender_event_id),
        )
        mode = resolve_attack_roll_mode(
            attack.weapon,
            distance_ft,
            advantage_sources=attack_advantage,
            other_disadvantage_sources=disadvantage_total,
            close_enemy_active=close_enemy_active,
        )
        base_roll = roll_d20(
            dice,
            attack.attack_bonus + attack_roll_flat_bonus(attacker, attack.weapon.id),
            mode,
        )
        base_roll, heroic_reroll = reroll_failed_attack_with_heroic_inspiration(
            attacker, base_roll, effective_armor_class(defender), dice,
        )
        roll = apply_d20_bonus_dice(
            attacker, ModifierKind.ATTACK_ROLL_BONUS_DIE, base_roll, dice,
        )
        d20_bonus_source_name = None
        if base_roll.selected_roll != 1:
            roll, d20_bonus_source_name = apply_d20_bonus_die_if_useful(
                attacker, "attack", roll, effective_armor_class(defender), dice, round_number,
            )
        consume_next_attack_against_advantage(attacker, defender_event_id)
        consume_sap(attacker)
        consume_attacks_against_advantage(defender)
        extend_rage_from_attack(attacker, round_number)
        return AttackRollResolution(
            roll=roll,
            mode=mode,
            heroic_reroll=heroic_reroll,
            brutal_strike_disadvantage=brutal_disadvantage,
            d20_bonus_source_name=d20_bonus_source_name,
        )
    except Exception as exc:
        logger.exception("Failed to resolve attack roll for %s.", attacker.template.name)
        raise RuntimeError("Attack roll could not be resolved.") from exc
