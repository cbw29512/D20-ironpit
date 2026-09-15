from __future__ import annotations

import logging

from app.combat.death_triggers import resolve_event_death_triggers
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def append_after_event(
    output: list[BattleEvent],
    sequence: int,
    round_number: int,
    event: BattleEvent,
    setup: EncounterSetup,
    dice: DiceProvider,
    resolved: set[str],
) -> int:
    """Append one causal event and settle its immediate on-death lifecycle."""
    try:
        output.append(event)
        triggered, sequence = resolve_event_death_triggers(
            sequence,
            round_number,
            event,
            setup,
            dice,
            resolved=resolved,
        )
        output.extend(triggered)
        return sequence
    except Exception as exc:
        logger.exception("Post-event death lifecycle failed after event %s.", event.sequence)
        raise RuntimeError("Post-event death lifecycle could not be resolved.") from exc
