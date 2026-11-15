"""Universal source-scoped replacement delay for destroyed Grapple appendages."""
from __future__ import annotations

import logging

from app.combat.grapple_queries import source_grapple_count
from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def _owner(setup: EncounterSetup, source_id: str):
    try:
        if setup is None or not source_id:
            raise ValueError("A broken appendage requires its active encounter and owner.")
        members = [
            member for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == source_id
        ]
        if len(members) != 1:
            raise ValueError("A broken appendage must have exactly one source owner.")
        return members[0]
    except Exception:
        logger.exception("Unable to resolve Grapple appendage source owner.")
        raise


def source_grapple_capacity_used(
    setup: EncounterSetup, source_id: str, effect_id: str,
) -> int:
    """Active held targets plus this source action's until-next-turn losses."""
    try:
        if not effect_id:
            raise ValueError("Source appendage capacity needs an effect ID.")
        owner = _owner(setup, source_id)
        count = owner.state.broken_grapple_appendages.get(effect_id, 0)
        if count < 0:
            raise ValueError("Broken Grapple appendage counts cannot be negative.")
        return source_grapple_count(setup, source_id) + count
    except Exception:
        logger.exception("Failed to count source-owned broken Grapple slots.")
        raise


def record_broken_grapple_appendage(
    setup: EncounterSetup, source_id: str, effect_id: str,
) -> None:
    """Consume one source slot now; begin_turn restores all on its next turn."""
    try:
        if not effect_id:
            raise ValueError("Destroyed Grapple appendage lacks a linked source action.")
        owner = _owner(setup, source_id)
        bucket = owner.state.broken_grapple_appendages
        bucket[effect_id] = bucket.get(effect_id, 0) + 1
    except Exception:
        logger.exception("Failed to record source-owned Grapple appendage destruction.")
        raise
