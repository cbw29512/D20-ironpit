from __future__ import annotations

from dataclasses import dataclass

from app.combat.attack_legality import attack_is_automatic_hit
from app.combat.bloodied import bloodied_fury_advantage
from app.combat.conditions import attack_roll_condition_sources
from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.d20_effects import strength_d20_disadvantage
from app.combat.dice import DiceProvider
from app.combat.heroic_inspiration import reroll_failed_attack_with_heroic_inspiration
from app.combat.modifier_stack import (
    apply_d20_bonus_dice,
    attacks_against_advantage_sources,
    effective_armor_class,
    next_attack_against_advantage_sources,
)
from app.combat.range import resolve_attack_roll_mode
from app.combat.reckless_attack import attacks_against_reckless_advantage, reckless_attack_advantage
from app.combat.rolls import roll_d20
from app.combat.sap import sap_disadvantage
from app.domain.models import CombatantState, DiceRoll, RollMode, WeaponAttack
from app.domain.modifiers import ModifierKind


@dataclass(frozen=True)
class AttackRollPhase:
    automatic_hit: bool
    mode: RollMode
    attack_roll: DiceRoll | None
    heroic_reroll: bool
    natural: int
    natural_20: bool
    natural_1: bool
    expanded_critical: bool


def resolve_attack_roll_phase(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    attacker_event_id: str,
    defender_event_id: str,
    advantage_sources: int,
    other_disadvantage_sources: int,
    close_enemy_active: bool,
) -> AttackRollPhase:
    automatic_hit = attack_is_automatic_hit(attack, attacker_event_id, defender)
    if automatic_hit:
        return AttackRollPhase(True, RollMode.NORMAL, None, False, 0, False, False, False)
    condition_advantage, condition_disadvantage = attack_roll_condition_sources(
        attacker, defender, distance_ft, defender_event_id,
    )
    mode = resolve_attack_roll_mode(
        attack.weapon,
        distance_ft,
        advantage_sources=(
            advantage_sources + condition_advantage + bloodied_fury_advantage(attacker, attack)
            + attacks_against_advantage_sources(defender) + attacks_against_reckless_advantage(defender)
            + reckless_attack_advantage(attacker, attack)
            + conditional_attack_advantage_sources(attack, defender, attacker_event_id)
            + next_attack_against_advantage_sources(attacker, defender_event_id)
        ),
        other_disadvantage_sources=(
            other_disadvantage_sources + condition_disadvantage + sap_disadvantage(attacker)
            + int("Poor Depth Perception" in attacker.template.source_trait_names and distance_ft > 30)
            + int(attack.attack_ability == "strength") * strength_d20_disadvantage(attacker)
        ),
        close_enemy_active=close_enemy_active,
    )
    base_roll = roll_d20(dice, attack.attack_bonus, mode)
    base_roll, heroic_reroll = reroll_failed_attack_with_heroic_inspiration(
        attacker, base_roll, effective_armor_class(defender), dice,
    )
    attack_roll = apply_d20_bonus_dice(attacker, ModifierKind.ATTACK_ROLL_BONUS_DIE, base_roll, dice)
    natural = attack_roll.selected_roll or 0
    return AttackRollPhase(
        automatic_hit=False,
        mode=mode,
        attack_roll=attack_roll,
        heroic_reroll=heroic_reroll,
        natural=natural,
        natural_20=natural == 20,
        natural_1=natural == 1,
        expanded_critical=natural >= attacker.template.progression_features.critical_hit_minimum,
    )
