from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def note_damage_source(
    state: CombatantState,
    amount: int,
    source_id: str | None,
) -> None:
    """Record actual damage taken from one identified combat source this turn."""
    try:
        if amount <= 0 or source_id is None:
            return
        normalized = source_id.strip()
        if not normalized:
            raise ValueError("Damage source id cannot be blank.")
        ledger = state.damage_taken_this_turn_by_source
        ledger[normalized] = ledger.get(normalized, 0) + amount
    except Exception:
        logger.exception(
            "Failed to record damage source %r for %s.",
            source_id,
            state.template.name,
        )
        raise
