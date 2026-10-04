from __future__ import annotations

import logging

from app.combat.persistent_save_zone_resolution import expire_save_zones, resolve_save_zone_trigger
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def resolve_save_zone_window(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
    trigger: str,
) -> tuple[list, int]:
    try:
        expire_save_zones(setup, round_number)
        events = []
        for zone in list(setup.save_zones):
            more, sequence = resolve_save_zone_trigger(
                sequence, round_number, member, setup, zone, dice, turn_key, trigger,
            )
            events.extend(more)
        return events, sequence
    except Exception:
        logger.exception("Failed save-zone window %s for %s.", trigger, member.combatant_id)
        raise
