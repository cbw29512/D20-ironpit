"""Generic source-owned Grapple penalties for ability checks and saving throws.

The penalty exists only while the source Grapple remains in fight state.
Attack rolls are deliberately excluded; source rules must opt into those
independently. No monster name is consulted by this resolver.
"""
from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def grapple_check_save_disadvantage_sources(
    state: CombatantState, ability: str | None,
) -> int:
    try:
        if not ability:
            return 0
        wanted = ability.strip().casefold()
        return sum(
            wanted in source.check_save_disadvantage_abilities
            for source in state.grapple_sources
        )
    except Exception:
        logger.exception("Failed Grapple check/save penalty lookup for %s", state.template.name)
        raise
