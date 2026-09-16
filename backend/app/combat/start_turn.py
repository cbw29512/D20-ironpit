from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.recharge import resolve_recharge_checks
from app.combat.state import begin_turn
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def begin_turn_with_events(
    sequence: int,
    round_number: int,
    actor_id: str,
    state: CombatantState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Initialize a turn and resolve auditable start-of-turn resource checks."""
    try:
        begin_turn(state)
        events: list[BattleEvent] = []
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
