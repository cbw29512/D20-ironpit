from __future__ import annotations

from dataclasses import dataclass

from app.combat.condition_immunity import condition_is_immune
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.content.character_math import proficiency_bonus
from app.domain.models import CombatantState, DiceRoll
from app.domain.size import CreatureSize, size_at_most

FEATURE_ID = "cunning-strike-trip"
PRONE_EFFECT_ID = "prone"


@dataclass(frozen=True)
class CunningStrikeTripResolution:
    save_roll: DiceRoll | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied: bool = False


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
