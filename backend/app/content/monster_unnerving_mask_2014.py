from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.reactions import TurnStartSaveConditionReaction

logger = logging.getLogger(__name__)


def supports_unnerving_mask_reaction_2014(monster: SourceMonster2014) -> bool:
    """Require pinned 2014 source evidence before binding the shared Reaction."""
    try:
        text = (monster.source_reactions or "").casefold()
        return (
            monster.reaction_names == ["Unnerving Mask"]
            and "dc 14" in text
            and "wisdom" in text
            and "frightened until the end of its turn" in text
            and "30 feet" in text
            and "creature the devil can see" in text
            and "if the creature can see the devil" in text
        )
    except Exception:
        logger.exception("Failed to verify Unnerving Mask for %s.", monster.id)
        raise


def source_unnerving_mask_reaction_2014(
    monster: SourceMonster2014,
) -> TurnStartSaveConditionReaction | None:
    try:
        if not supports_unnerving_mask_reaction_2014(monster):
            return None
        return TurnStartSaveConditionReaction(
            source_id="unnerving-mask",
            source_name="Unnerving Mask",
            range_ft=30,
            save_ability="wisdom",
            save_dc=14,
            condition_id="frightened",
            expiry_timing="target_turn_end",
            requires_source_can_see_target=True,
            requires_target_can_see_source=True,
        )
    except Exception:
        logger.exception("Failed to bind Unnerving Mask for %s.", monster.id)
        raise
