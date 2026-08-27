from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def roll_initiative_order(
    sequence: int,
    states: list[CombatantState],
    dice: DiceProvider,
) -> tuple[list[BattleEvent], list[CombatantState], int]:
    try:
        events: list[BattleEvent] = []
        for state in states:
            initiative = roll_d20(dice, state.template.initiative_bonus)
            state.initiative_roll = initiative.selected_roll
            state.initiative_total = initiative.total
            events.append(BattleEvent(
                sequence=sequence + len(events),
                round_number=0,
                event_type="initiative",
                actor_id=state.instance_id,
                actor_name=state.template.name,
                attack_roll=initiative,
                animation="initiative",
                description=f"{state.template.name} rolls initiative {state.initiative_total}.",
            ))

        order = sorted(
            states,
            key=lambda state: (
                -(state.initiative_total or 0),
                -state.template.initiative_bonus,
                state.instance_id,
            ),
        )
        return events, order, sequence + len(events)
    except Exception as exc:
        logger.exception("Initiative resolution failed for encounter roster.")
        raise RuntimeError("Initiative order could not be resolved.") from exc
