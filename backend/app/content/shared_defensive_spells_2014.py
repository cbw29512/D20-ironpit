from __future__ import annotations

import logging

from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"


def longstrider_2014() -> DefensiveSpellAction:
    """One-hour non-concentration speed buff used by any legal 2014 caster."""
    try:
        return DefensiveSpellAction(
            id="longstrider",
            name="Longstrider",
            level=1,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="self",
            target_count=1,
            modifier_effects=[SpellModifierEffect(kind="speed", flat_bonus=10)],
            concentration=False,
            priority=10,
            animation="longstrider",
            source=f"{_SOURCE}: Longstrider",
        )
    except Exception:
        logger.exception("Failed to compile shared 2014 Longstrider.")
        raise
