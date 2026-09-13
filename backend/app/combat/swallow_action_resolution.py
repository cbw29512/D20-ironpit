from __future__ import annotations

import logging

from app.combat.swallow import choose_swallow, resolve_swallow
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_priority_swallow_action(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int, bool]:
    try:
        choice = choose_swallow(source, setup)
        if choice is None:
            return [], sequence, False
        target, action = choice
        event = resolve_swallow(sequence, round_number, source, target, action, setup)
        return [event], sequence + 1, True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed priority Swallow stage for %s.", source.combatant_id)
        raise RuntimeError("Priority Swallow action could not be resolved.") from exc
