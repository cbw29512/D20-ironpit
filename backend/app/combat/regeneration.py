from __future__ import annotations

import logging

from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def apply_start_of_turn_regeneration(state: CombatantState) -> tuple[int, bool, bool]:
    """Resolve start-of-turn Regeneration. Returns healed, died, suppressed."""
    try:
        trait = state.template.regeneration
        if trait is None:
            return 0, False, False
        taken = set(state.damage_types_taken_since_regen)
        state.damage_types_taken_since_regen = []
        suppressed = trait.suppressed_by(taken)
        if suppressed or (trait.requires_positive_hp and state.current_hp <= 0):
            if trait.survives_zero_until_turn and state.current_hp <= 0 and not state.is_dead:
                state.current_hp = 0
                state.is_alive = False
                state.is_dead = True
                state.is_unconscious = False
                state.is_stable = False
                return 0, True, suppressed
            return 0, False, suppressed
        healed = restore_hit_points(state, trait.amount)
        return healed, False, False
    except Exception:
        logger.exception("Failed start-of-turn Regeneration for %s.", state.template.name)
        raise


def resolve_start_of_turn_regeneration(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Emit one start-of-turn Regeneration event when the trait exists."""
    try:
        trait = member.state.template.regeneration
        if trait is None:
            return [], sequence
        hp_before = member.state.current_hp
        healed, died, suppressed = apply_start_of_turn_regeneration(member.state)
        if died:
            description = (
                f"{member.state.template.name} starts the turn at 0 HP without "
                f"{trait.source_name} and dies."
            )
        elif suppressed:
            description = (
                f"{member.state.template.name}'s {trait.source_name} does not function "
                "this turn."
            )
        elif healed:
            description = (
                f"{member.state.template.name} regains {healed} hit points from "
                f"{trait.source_name}."
            )
        else:
            return [], sequence
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            feature_id=trait.source_name.lower().replace(" ", "-"),
            hp_before=hp_before,
            hp_after=member.state.current_hp,
            is_dead=member.state.is_dead,
            animation="feature",
            description=description,
        )
        return [event], sequence + 1
    except Exception:
        logger.exception("Failed Regeneration event for %s.", member.combatant_id)
        raise
