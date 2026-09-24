from __future__ import annotations

import logging

from app.domain.persistent_hazards import PersistentHazardAction
from app.domain.size import CreatureSize
from app.domain.spells import DefensiveSpellAction
from app.domain.zero_hp_effects import SurvivalWard

logger = logging.getLogger(__name__)


def death_ward_2014() -> DefensiveSpellAction:
    """Compile 2014 Death Ward onto the generic one-shot survival-ward primitive."""
    try:
        return DefensiveSpellAction(
            id="death-ward",
            name="Death Ward",
            level=4,
            action_cost="action",
            range_ft=5,
            duration_minutes=480,
            target_policy="friendly",
            survival_ward=SurvivalWard(
                replacement_hp=1,
                prevents_nondamage_instant_death=True,
            ),
            priority=40,
            animation="death-ward",
            source="D&D Basic Rules 2014: Death Ward",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Death Ward.")
        raise


def guardian_of_faith_2014(save_dc: int) -> PersistentHazardAction:
    """Compile 2014 Guardian of Faith onto the generic stationary hazard primitive."""
    try:
        return PersistentHazardAction(
            id="guardian-of-faith",
            name="Guardian of Faith",
            level=4,
            action_cost="action",
            cast_range_ft=30,
            duration_rounds=4800,
            footprint_size=CreatureSize.LARGE,
            trigger_radius_ft=10,
            save_ability="dexterity",
            dc=save_dc,
            failure_damage=20,
            success_damage=10,
            damage_type="radiant",
            max_total_damage=60,
            animation="guardian-of-faith",
            source="D&D Basic Rules 2014: Guardian of Faith",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Guardian of Faith.")
        raise
