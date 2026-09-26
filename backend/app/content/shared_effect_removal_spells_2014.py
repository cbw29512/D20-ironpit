from __future__ import annotations

import logging

from app.domain.actions import AbilityName
from app.domain.effect_removal import EffectRemovalAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014: Dispel Magic"


def dispel_magic_2014(casting_ability: AbilityName) -> EffectRemovalAction:
    """Build 2014 Dispel Magic through the universal persistent-effect removal action."""
    try:
        return EffectRemovalAction(
            id="dispel-magic",
            name="Dispel Magic",
            level=3,
            action_cost="action",
            range_ft=120,
            casting_ability=casting_ability,
            target_mode="enemy",
            auto_remove_max_level=3,
            resource_id="spell-slot-3",
            resource_cost=1,
            expends_spell_slot=True,
            animation="dispel-magic",
        )
    except Exception:
        logger.exception("Failed to build 2014 Dispel Magic for %s casting.", casting_ability)
        raise
