from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.resources import recharge_start_events
from app.combat.state import begin_turn
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_turn_start_resources(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Apply universal start-of-turn state and emit auditable resource events."""
    try:
        begin_turn(attacker.state)
        return recharge_start_events(
            sequence,
            round_number,
            attacker.state,
            attacker.combatant_id,
            dice,
        )
    except Exception:
        logger.exception(
            "Failed to resolve start-of-turn resources for %s.",
            attacker.combatant_id,
        )
        raise
