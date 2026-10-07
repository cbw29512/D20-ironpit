from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.recharge import resolve_recharge_checks
from app.combat.state import begin_turn
from app.combat.turn_start_conditions import turn_start_condition_events
from app.combat.turn_start_targeting_overrides import resolve_turn_start_targeting_overrides
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, CombatantState, DiceRoll

logger = logging.getLogger(__name__)


def begin_turn_with_events(
    sequence: int,
    round_number: int,
    actor_id: str,
    state: CombatantState,
    dice: DiceProvider,
    member: EncounterCombatant | None = None,
) -> tuple[list[BattleEvent], int]:
    """Initialize a turn and resolve auditable start-of-turn resource checks."""
    try:
        countered = begin_turn(state)
        events: list[BattleEvent] = []
        if member is not None:
            checked, sequence = turn_start_condition_events(sequence, round_number, member)
            events.extend(checked)
        for debuff_id, source_id, movement_cost in countered:
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor_id,
                actor_name=state.template.name,
                target_id=source_id,
                removed_condition_ids=[debuff_id],
                movement_ft=movement_cost,
                feature_id="debuff-counter",
                animation="condition-ended",
                description=(
                    f"{state.template.name} spends {movement_cost} feet of movement to clear {debuff_id} "
                    "using an active buff."
                ),
            ))
            sequence += 1
        for check in resolve_turn_start_targeting_overrides(state, dice):
            outcome = "activates" if check.activated else "does not activate"
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor_id,
                actor_name=state.template.name,
                feature_id=check.source_id,
                feature_roll=DiceRoll(
                    notation=f"1d{check.die_size}",
                    rolls=[check.roll],
                    selected_roll=check.roll,
                    total=check.roll,
                ),
                animation="feature",
                description=(
                    f"{state.template.name} rolls {check.roll} for {check.source_name}: "
                    f"{check.source_name} {outcome}."
                ),
            ))
            sequence += 1
        for check in resolve_recharge_checks(state, dice):
            threshold = (
                str(check.minimum_roll)
                if check.minimum_roll == 6
                else f"{check.minimum_roll}-6"
            )
            result = "recharges" if check.restored else "does not recharge"
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor_id,
                actor_name=state.template.name,
                feature_id=f"recharge:{check.resource_id}",
                resource_remaining=check.resource_remaining,
                animation="feature",
                description=(
                    f"{state.template.name} rolls {check.roll} for Recharge {threshold}: "
                    f"{check.resource_id} {result}."
                ),
            ))
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Start-of-turn resolution failed for %s.", state.template.name)
        raise RuntimeError("Start-of-turn effects could not be resolved.") from exc
