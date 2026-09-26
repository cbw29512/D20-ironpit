from __future__ import annotations

import logging

from app.content.druid_land_2014_level10 import natures_ward_debuff_counters_2014
from app.domain.debuffs import DebuffCounter
from app.domain.progression import (
    PassiveDebuffCounterGrant,
    ProgressionCombatFeatures,
    SavingThrowAdvantageGrant,
)

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def druid_land_progression_features_2014(level: int) -> ProgressionCombatFeatures:
    """Compile Land Druid passives as data for shared combat checks."""
    try:
        save_advantage = [
            SavingThrowAdvantageGrant(
                source_id="fey-ancestry",
                source_name="Fey Ancestry",
                abilities=_ABILITIES,
                required_effect_tags=["charm"],
            ),
        ]
        debuff_counters: list[PassiveDebuffCounterGrant] = []
        if level >= 6:
            save_advantage.append(SavingThrowAdvantageGrant(
                source_id="lands-stride",
                source_name="Land's Stride",
                abilities=_ABILITIES,
                requires_magical_effect=True,
                required_effect_tags=["plant-impediment"],
            ))
            debuff_counters.append(PassiveDebuffCounterGrant(
                source_id="lands-stride",
                source_name="Land's Stride",
                counter=DebuffCounter(
                    debuff_id="difficult-terrain",
                    source_scope="nonmagical",
                ),
            ))
        if level >= 10:
            debuff_counters.extend(natures_ward_debuff_counters_2014())
        return ProgressionCombatFeatures(
            saving_throw_advantage_grants=save_advantage,
            passive_debuff_counter_grants=debuff_counters,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Land Druid passive check bindings at level %s.", level)
        raise
