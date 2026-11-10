"""2014 spell facts supplied by pinned spell source; no monster runtime dispatch."""
from __future__ import annotations

import logging

from app.content.monster_sleep_spell_source_2014 import sleep_spell_rules_2014
from app.domain.hit_point_pool_spells import HitPointPoolSpellAction

logger = logging.getLogger(__name__)


def sleep_2014() -> HitPointPoolSpellAction:
    """Build the 2014 Sleep spell from its edition-specific immutable rules."""
    try:
        source = sleep_spell_rules_2014()
        return HitPointPoolSpellAction(
            id=source.spell_id,
            name="Sleep",
            level=source.spell_level,
            action_cost=source.casting_action,
            range_ft=source.range_ft,
            area_radius_ft=source.area_radius_ft,
            pool_dice_count=source.pool_dice_count,
            pool_dice_size=source.pool_dice_size,
            extra_dice_per_upcast_level=source.pool_extra_dice_per_upcast_level,
            target_order=source.target_order,
            condition_id=source.condition_id,
            duration_rounds=source.duration_rounds,
            skip_unconscious=source.skip_unconscious,
            ends_on_damage=source.ends_on_damage,
            excluded_creature_types=list(source.excluded_creature_types),
            excluded_condition_immunities=list(source.excluded_condition_immunities),
            allowed_removal_action_ids=list(source.allowed_removal_action_ids),
            animation="sleep",
            source=source.source_url,
        )
    except Exception:
        logger.exception("Failed to compile source-pinned 2014 Sleep.")
        raise
