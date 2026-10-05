from __future__ import annotations

import logging

from app.combat.bloodied import is_bloodied
from app.combat.debuff_answers import active_condition_ids, suppressed_condition_ids
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def turn_start_condition_events(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Audit active and suppressed conditions before the creature acts."""
    try:
        events: list[BattleEvent] = []
        state = member.state
        for condition_id in active_condition_ids(state):
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=state.template.name,
                applied_condition_ids=[condition_id],
                feature_id="turn-start-condition",
                animation="condition",
                description=f"{state.template.name} begins the turn {condition_id}.",
            ))
            sequence += 1
        for condition_id in suppressed_condition_ids(state):
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=state.template.name,
                feature_id="turn-start-condition-suppressed",
                animation="condition-ended",
                description=(
                    f"{state.template.name} begins the turn with {condition_id} "
                    "suppressed by an active buff."
                ),
            ))
            sequence += 1
        if is_bloodied(state):
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=state.template.name,
                feature_id="turn-start-bloodied",
                animation="condition",
                description=f"{state.template.name} begins the turn Bloodied.",
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed turn-start condition audit for %s.", member.combatant_id)
        raise
