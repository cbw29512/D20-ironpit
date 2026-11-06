"""Universal action to end source-proven burning recurring damage.

2014 Magmin Touch: "Until a creature takes an action to douse the fire..."
The pinned source supplies no range, actor restriction, or other qualifier.
Any living creature may therefore take the action against any burning target.
No range or adjacency is invented.
"""
from __future__ import annotations

import logging

from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def douse_burning(target, actor_id: str, round_number: int) -> list[BattleEvent]:
    """Remove the nonstacking burning timed effect. Source owns the effect_id."""
    try:
        removed = [
            effect for effect in list(target.timed_effects)
            if effect.effect_id == "burning"
        ]
        if not removed:
            return []
        for effect in removed:
            target.timed_effects.remove(effect)
            if effect.effect_id in target.active_effect_ids:
                target.active_effect_ids.remove(effect.effect_id)
        return [BattleEvent(
            sequence=0,  # caller assigns
            event_type="feature",
            round_number=round_number,
            actor_id=actor_id, actor_name="douse",
            target_id=getattr(target, "id", None),
            feature_id="douse-burning",
            animation="none",
            description="A creature takes an action to douse the fire.",
        )]
    except Exception:
        logger.exception("Douse burning failed for actor %s.", actor_id)
        raise
