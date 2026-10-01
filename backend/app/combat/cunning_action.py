from __future__ import annotations

import logging

from app.combat.tactical_actions import (
    choose_offensive_dash_grant,
    resolve_bonus_tactical_grant,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
CUNNING_DASH_ID = "cunning-action-dash"


def needs_dash(member: EncounterCombatant, setup: EncounterSetup, turn_key: str) -> bool:
    """Compatibility query backed by the universal tactical-action chooser."""
    try:
        grant = choose_offensive_dash_grant(member, setup, turn_key)
        return grant is not None and grant.id == CUNNING_DASH_ID
    except Exception as exc:
        logger.exception("Failed Cunning Action Dash query for %s.", member.combatant_id)
        raise RuntimeError("Cunning Action Dash could not be evaluated.") from exc


def use_dash(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> BattleEvent | None:
    """Compatibility wrapper for existing Rogue tests and callers."""
    try:
        grant = choose_offensive_dash_grant(member, setup, turn_key)
        if grant is None or grant.id != CUNNING_DASH_ID:
            return None
        return resolve_bonus_tactical_grant(sequence, round_number, member, grant)
    except Exception as exc:
        logger.exception("Failed Cunning Action Dash for %s.", member.combatant_id)
        raise RuntimeError("Cunning Action Dash could not be resolved.") from exc
