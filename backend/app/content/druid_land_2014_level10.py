from __future__ import annotations

import logging

from app.domain.debuffs import DebuffCounter
from app.domain.passive_modifiers import PassiveModifierGrant
from app.domain.progression import PassiveDebuffCounterGrant

logger = logging.getLogger(__name__)

_PROTECTED_SOURCE_TYPES = ["elemental", "fey"]


def natures_ward_condition_immunities_2014() -> list[PassiveModifierGrant]:
    """Bind source-typed Charm/Fright immunity to the universal modifier pipeline."""
    try:
        return [
            PassiveModifierGrant(
                source_id="natures-ward",
                source_name="Nature's Ward",
                kind="condition-immunity",
                condition_id=condition_id,
                source_creature_types=list(_PROTECTED_SOURCE_TYPES),
            )
            for condition_id in ("charmed", "frightened")
        ]
    except Exception:
        logger.exception("Failed to compile 2014 Nature's Ward condition immunities.")
        raise


def natures_ward_debuff_counters_2014() -> list[PassiveDebuffCounterGrant]:
    """Bind unconditional Poisoned/disease prevention to the universal debuff check."""
    try:
        return [
            PassiveDebuffCounterGrant(
                source_id="natures-ward",
                source_name="Nature's Ward",
                counter=DebuffCounter(debuff_id=debuff_id, source_scope="any"),
            )
            for debuff_id in ("poisoned", "disease")
        ]
    except Exception:
        logger.exception("Failed to compile 2014 Nature's Ward debuff counters.")
        raise
