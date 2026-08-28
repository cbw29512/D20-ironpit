from __future__ import annotations

import logging
from collections.abc import Iterable

from app.combat.dice import DiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.precombat import resolve_precombat_setup
from app.domain.models import (
    BattleEvent,
    BattlefieldState,
    CombatantState,
    EncounterSetup,
)

logger = logging.getLogger(__name__)


def resolve_battle_start(
    combatants: Iterable[CombatantState],
    battlefield: BattlefieldState,
    dice: DiceProvider,
    setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], list[CombatantState], int]:
    try:
        states = list(combatants)
        events, surprised_actor_ids, sequence = resolve_precombat_setup(
            1, states, battlefield, dice, setup
        )
        initiative_events, order, sequence = roll_initiative_order(
            states,
            dice,
            sequence=sequence,
            surprised_actor_ids=surprised_actor_ids,
        )
        events.extend(initiative_events)
        return events, order, sequence
    except Exception as exc:
        logger.exception("Battle-start resolution failed.")
        raise RuntimeError("Battle start could not be resolved.") from exc
