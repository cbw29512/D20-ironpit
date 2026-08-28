from __future__ import annotations

import logging
from collections.abc import Iterable

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def roll_initiative_order(
    states: Iterable[CombatantState],
    dice: DiceProvider,
    sequence: int = 1,
) -> tuple[list[BattleEvent], list[CombatantState], int]:
    try:
        combatants = list(states)
        events: list[BattleEvent] = []
        for state in combatants:
            initiative = roll_d20(dice, state.template.initiative_bonus)
            state.initiative_roll = initiative.selected_roll
            state.initiative_total = initiative.total
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="initiative",
                actor_id=state.template.id,
                actor_name=state.template.name,
                attack_roll=initiative,
                animation="initiative",
                description=f"{state.template.name} rolls initiative {state.initiative_total}.",
            ))
            sequence += 1

        order = sorted(
            combatants,
            key=lambda state: (state.initiative_total or 0, state.template.initiative_bonus),
            reverse=True,
        )
        return events, order, sequence
    except Exception as exc:
        logger.exception("Initiative resolution failed.")
        raise RuntimeError("Initiative could not be resolved.") from exc
