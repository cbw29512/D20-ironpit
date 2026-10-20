from __future__ import annotations

import logging

from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState
from app.domain.runtime import TimedTurnBehavior

logger = logging.getLogger(__name__)
FORCED_APPROACH_DISTANCE_FT = 5


def forced_retreat_active(state: CombatantState) -> bool:
    return any(effect.turn_behavior == "forced_retreat" for effect in state.timed_effects)


def forced_approach_active(state: CombatantState) -> bool:
    return any(effect.turn_behavior == "forced_approach_source" for effect in state.timed_effects)


def resolve_forced_approach(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Spend ordinary movement to approach the one active effect source."""
    try:
        effects = [effect for effect in member.state.timed_effects
                   if effect.turn_behavior == "forced_approach_source"]
        if not effects:
            return [], sequence
        source_ids = {effect.source_id for effect in effects}
        if len(source_ids) != 1:
            raise ValueError("Compelled approach requires exactly one active source.")
        source_id = next(iter(source_ids))
        sources = [actor for actor in [*setup.heroes, *setup.monsters]
                   if actor.combatant_id == source_id]
        if len(sources) != 1:
            raise ValueError("Compelled approach source is not present in the encounter.")
        events, sequence, _ = move_toward_with_reactions(
            sequence, round_number, member, sources[0], setup,
            FORCED_APPROACH_DISTANCE_FT, dice, movement_source="speed",
            turn_key=turn_key, compelled=True,
        )
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Compelled approach failed for %s.", member.combatant_id)
        raise RuntimeError("Compelled approach could not be resolved.") from exc


def build_forced_retreat_event(sequence: int, round_number: int, combatant_id: str, state: CombatantState) -> BattleEvent:
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=combatant_id, actor_name=state.template.name,
        target_id=combatant_id, target_name=state.template.name,
        feature_id="forced-retreat", animation="forced-retreat",
        description=f"{state.template.name} spends the turn fleeing; Iron Pit keeps the card in its formation slot.",
    )


def apply_ongoing_spell_condition(
    target: CombatantState,
    condition_id: str,
    source_id: str,
    spell_id: str,
    save_ability: AbilityName,
    save_dc: int,
    *,
    applied_round: int,
    expiry_timing: ConditionTiming | None = None,
    allowed_removal_action_ids: list[str] | None = None,
    affected_states: list[CombatantState] | None = None,
    turn_behavior: TimedTurnBehavior = "normal",
) -> str | None:
    """Apply ongoing harmful spell control with Iron Pit's end-of-turn repeat-save rule."""
    if not spell_id:
        raise ValueError("Ongoing spell control requires a spell id.")
    if save_dc < 1:
        raise ValueError("Ongoing spell control requires a valid save DC.")
    return apply_timed_condition(
        target, condition_id, source_id, source_effect_id=spell_id,
        applied_round=applied_round, expires_at_start_of_source_turn=False,
        expiry_timing=expiry_timing, repeat_save_ability=save_ability,
        repeat_save_dc=save_dc, repeat_save_timing="target_turn_end",
        allowed_removal_action_ids=allowed_removal_action_ids,
        affected_states=affected_states, turn_behavior=turn_behavior,
    )
