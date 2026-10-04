from __future__ import annotations

import logging

from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import has_condition
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.rolls import roll_d20
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, TimedEffect

logger = logging.getLogger(__name__)
FRIGHTENED_EFFECT_ID = "frightened"
POISONED_EFFECT_ID = "poisoned"


def escape_check_effects(state: CombatantState) -> list[TimedEffect]:
    try:
        return [
            effect for effect in state.timed_effects
            if effect.escape_check_ability and effect.escape_check_dc is not None
        ]
    except Exception:
        logger.exception("Failed to list escape-check effects for %s.", state.template.name)
        raise


def should_escape_check(state: CombatantState) -> bool:
    try:
        return is_available(state, "action") and bool(escape_check_effects(state))
    except Exception:
        logger.exception("Failed to classify escape-check opportunity for %s.", state.template.name)
        raise


def ability_check_bonus(state: CombatantState, ability: str) -> int:
    scores = state.template.ability_scores
    if scores is None:
        raise ValueError(f"{state.template.name} lacks ability scores for a {ability} check.")
    return scores.modifier(ability)  # type: ignore[arg-type]


def resolve_escape_check(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    dice,
    *,
    setup: EncounterSetup | None = None,
) -> BattleEvent:
    """Spend an Action on a printed Strength/ability check to end a restraining effect."""
    try:
        if not is_available(actor.state, "action"):
            raise ValueError("Action is not available to attempt an escape check.")
        effect = escape_check_effects(actor.state)[0]
        ability = effect.escape_check_ability
        dc = effect.escape_check_dc
        if ability is None or dc is None:
            raise ValueError(f"{actor.state.template.name} escape check is missing ability or DC.")
        disadvantage = ability_check_disadvantage_sources(actor.state)
        disadvantage += int(
            has_condition(actor.state, POISONED_EFFECT_ID)
            or has_condition(actor.state, FRIGHTENED_EFFECT_ID)
        )
        mode = ability_check_roll_mode(
            actor.state,
            disadvantage_sources=disadvantage,
        )
        check = roll_d20(dice, ability_check_bonus(actor.state, ability) + d20_modifier(actor.state), mode)
        check, success = resolve_ability_check_outcome(
            actor.state,
            ability,  # type: ignore[arg-type]
            check,
            dc,
            dice=dice,
            round_number=round_number,
            encounter_roller=actor,
            setup=setup,
        )
        spend(actor.state, "action")
        if success:
            remove_effect_instance(actor.state, effect)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            ability_check_roll=check,
            check_ability=ability,
            check_dc=dc,
            check_succeeded=success,
            feature_id="escape-check",
            animation="escape-check",
            removed_condition_ids=[effect.effect_id] if success else [],
            description=(
                f"{actor.state.template.name} {'escapes' if success else 'fails to escape'} "
                f"{effect.effect_id} with a {ability.title()} check against DC {dc}."
            ),
        )
    except Exception:
        logger.exception("Failed escape check for %s.", actor.combatant_id)
        raise
