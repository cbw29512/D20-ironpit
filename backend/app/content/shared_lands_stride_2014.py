from __future__ import annotations

import logging

from app.domain.debuffs import DebuffCounter
from app.domain.progression import PassiveDebuffCounterGrant, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def lands_stride_2014() -> tuple[SavingThrowAdvantageGrant, PassiveDebuffCounterGrant]:
    """Compile the shared 2014 Land's Stride mechanics as universal check data."""
    try:
        return (
            SavingThrowAdvantageGrant(
                source_id="lands-stride",
                source_name="Land's Stride",
                abilities=list(_ABILITIES),
                requires_magical_effect=True,
                required_effect_tags=["plant-impediment"],
            ),
            PassiveDebuffCounterGrant(
                source_id="lands-stride",
                source_name="Land's Stride",
                counter=DebuffCounter(
                    debuff_id="difficult-terrain",
                    source_scope="nonmagical",
                ),
            ),
        )
    except Exception:
        logger.exception("Failed to compile shared 2014 Land's Stride mechanics.")
        raise
