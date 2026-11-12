from __future__ import annotations

import logging

from app.domain.debuffs import DebuffCounter
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)


def freedom_of_movement_debuff_counters_2014(
    *, prevents_magical_paralysis: bool,
) -> list[DebuffCounter]:
    """Compose the shared 2014 movement counters from source-owned qualifiers."""
    try:
        counters = [
            DebuffCounter(debuff_id="difficult-terrain"),
            DebuffCounter(debuff_id="speed-reduction", source_scope="magical"),
            DebuffCounter(debuff_id="restrained", source_scope="magical"),
            DebuffCounter(
                debuff_id="grappled",
                source_scope="nonmagical",
                mode="remove-with-movement",
                movement_cost_ft=5,
            ),
            DebuffCounter(
                debuff_id="restrained",
                source_scope="nonmagical",
                mode="remove-with-movement",
                movement_cost_ft=5,
            ),
        ]
        if prevents_magical_paralysis:
            counters.insert(3, DebuffCounter(debuff_id="paralyzed", source_scope="magical"))
        return counters
    except Exception:
        logger.exception("Failed to compose shared 2014 Freedom of Movement counters.")
        raise


def freedom_of_movement_2014() -> DefensiveSpellAction:
    """Build shared 2014 Freedom of Movement from universal debuff counters."""
    try:
        counters = freedom_of_movement_debuff_counters_2014(
            prevents_magical_paralysis=True,
        )
        return DefensiveSpellAction(
            id="freedom-of-movement",
            name="Freedom of Movement",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=60,
            target_policy="friendly",
            target_count=1,
            concentration=False,
            priority=85,
            modifier_effects=[
                SpellModifierEffect(kind="debuff-counter", debuff_counter=counter)
                for counter in counters
            ],
            animation="freedom-of-movement",
            source="D&D Basic Rules 2014: Freedom of Movement",
        )
    except Exception:
        logger.exception("Failed to build shared 2014 Freedom of Movement.")
        raise
