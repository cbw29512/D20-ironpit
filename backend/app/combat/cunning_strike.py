from __future__ import annotations

from dataclasses import dataclass

from app.combat.condition_immunity import condition_is_immune
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.content.character_math import proficiency_bonus
from app.domain.models import CombatantState, DiceRoll
from app.domain.size import CreatureSize, size_at_most

FEATURE_ID = "cunning-strike-trip"
OBSCURE_FEATURE_ID = "cunning-strike-obscure"
PRONE_EFFECT_ID = "prone"
BLINDED_EFFECT_ID = "blinded"


@dataclass(frozen=True)
class CunningStrikeTripResolution:
    save_roll: DiceRoll | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied: bool = False


@dataclass(frozen=True)
class CunningStrikeObscureResolution:
    save_roll: DiceRoll | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied: bool = False


def select_obscure_die_cost(
    attacker: CombatantState,
    defender: CombatantState | None,
    turn_key: str,
) -> int:
    """Select Obscure only when the universal Blinded condition can affect the target."""
    cost = attacker.template.progression_features.cunning_strike_obscure_die_cost
    if cost <= 0 or defender is None:
        return 0
    if attacker.template.progression_features.sneak_attack_d6 < cost:
        return 0
    if BLINDED_EFFECT_ID in defender.active_effect_ids:
        return 0
    if condition_is_immune(defender, BLINDED_EFFECT_ID):
        return 0
    attacker.feature_last_turn_keys[OBSCURE_FEATURE_ID] = turn_key
    return cost


def select_canonical_die_cost(
    attacker: CombatantState,
    defender: CombatantState | None,
    turn_key: str,
) -> int:
    """Choose the supported Sneak Attack trade with the strongest useful arena effect."""
    obscure_cost = select_obscure_die_cost(attacker, defender, turn_key)
    if obscure_cost:
        return obscure_cost
    return select_trip_die_cost(attacker, defender, turn_key)


def select_trip_die_cost(
    attacker: CombatantState,
    defender: CombatantState | None,
    turn_key: str,
) -> int:
    """Select the canonical Trip option only when it can affect the current target."""
    cost = attacker.template.progression_features.cunning_strike_trip_die_cost
    if cost <= 0 or defender is None:
        return 0
    if attacker.template.progression_features.sneak_attack_d6 < cost:
        return 0
    if not size_at_most(defender.template.size, CreatureSize.LARGE):
        return 0
    if PRONE_EFFECT_ID in defender.active_effect_ids:
        return 0
    if condition_is_immune(defender, PRONE_EFFECT_ID):
        return 0
    attacker.feature_last_turn_keys[FEATURE_ID] = turn_key
    return cost


def resolve_trip(
    attacker: CombatantState,
    defender: CombatantState,
    dice,
    turn_key: str,
) -> CunningStrikeTripResolution:
    """Resolve the selected Trip save after Sneak Attack damage is dealt."""
    if attacker.feature_last_turn_keys.get(FEATURE_ID) != turn_key:
        return CunningStrikeTripResolution()
    if defender.is_dead:
        return CunningStrikeTripResolution()
    scores = attacker.template.ability_scores
    level = attacker.template.level
    if scores is None or level is None:
        raise ValueError("Cunning Strike requires certified ability scores and level.")
    dc = 8 + scores.modifier("dexterity") + proficiency_bonus(level)
    save_roll, succeeded = resolve_saving_throw(defender, "dexterity", dc, dice)
    applied = False
    if not succeeded and PRONE_EFFECT_ID not in defender.active_effect_ids:
        defender.active_effect_ids.append(PRONE_EFFECT_ID)
        applied = True
    return CunningStrikeTripResolution(save_roll, dc, succeeded, applied)



def resolve_obscure(
    attacker: CombatantState,
    defender: CombatantState,
    dice,
    turn_key: str,
) -> CunningStrikeObscureResolution:
    """Resolve Obscure with the shared Dexterity save and timed Blinded condition."""
    if attacker.feature_last_turn_keys.get(OBSCURE_FEATURE_ID) != turn_key:
        return CunningStrikeObscureResolution()
    if defender.is_dead:
        return CunningStrikeObscureResolution()
    scores = attacker.template.ability_scores
    level = attacker.template.level
    if scores is None or level is None:
        raise ValueError("Obscure requires certified ability scores and level.")
    dc = 8 + scores.modifier("dexterity") + proficiency_bonus(level)
    save_roll, succeeded = resolve_saving_throw(defender, "dexterity", dc, dice)
    applied = False
    if not succeeded:
        applied = apply_timed_condition(
            defender,
            BLINDED_EFFECT_ID,
            attacker.template.id,
            source_effect_id=OBSCURE_FEATURE_ID,
            expires_at_start_of_source_turn=False,
            expiry_timing="target_turn_end",
            use_default_poison_recovery=False,
        ) is not None
    return CunningStrikeObscureResolution(save_roll, dc, succeeded, applied)
