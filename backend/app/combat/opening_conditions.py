from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterSelection, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _roster(setup: EncounterSetup, side: str):
    return setup.heroes if side == "heroes" else setup.monsters


def member_at(setup: EncounterSetup, side: str, roster_index: int):
    try:
        roster = _roster(setup, side)
        if roster_index < 1 or roster_index > len(roster):
            raise ValueError(f"Opening condition roster index {roster_index} is outside {side}.")
        return roster[roster_index - 1]
    except Exception:
        logger.exception("Failed opening-condition roster lookup for %s #%s.", side, roster_index)
        raise


def apply_opening_conditions(setup: EncounterSetup, selection: EncounterSelection) -> None:
    """Apply declared starting conditions. Source cards stay immutable."""
    try:
        for binding in selection.opening_conditions:
            target = member_at(setup, binding.side, binding.roster_index)
            source = member_at(setup, binding.source_side, binding.source_roster_index)
            apply_timed_condition(
                target.state,
                binding.condition_id,
                source.combatant_id,
                source_template=source.state.template,
                source_is_magical=True,
                applied_round=0,
            )
    except Exception:
        logger.exception("Failed to apply opening conditions.")
        raise


def opening_condition_events(
    sequence: int,
    setup: EncounterSetup,
    selection: EncounterSelection,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        for binding in selection.opening_conditions:
            target = member_at(setup, binding.side, binding.roster_index)
            source = member_at(setup, binding.source_side, binding.source_roster_index)
            if binding.condition_id not in target.state.active_effect_ids:
                continue
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                applied_condition_ids=[binding.condition_id],
                feature_id="opening-condition",
                animation="condition",
                description=(
                    f"{target.state.template.name} begins the fight "
                    f"{binding.condition_id} because of {source.state.template.name}."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed to audit opening conditions.")
        raise
