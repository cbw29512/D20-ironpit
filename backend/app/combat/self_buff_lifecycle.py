from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp

logger = logging.getLogger(__name__)


def sync_hp_ended_self_buffs(state) -> list[str]:
    """End existing self-buff states whose source says full HP ends them."""
    try:
        if state.current_hp < effective_max_hp(state):
            return []
        ended = [
            action.id for action in state.template.timed_self_buff_actions
            if action.ends_at_full_hp and action.id in state.active_effect_ids
        ]
        if ended:
            state.active_effect_ids = [
                effect_id for effect_id in state.active_effect_ids if effect_id not in ended
            ]
            state.timed_effects = [
                effect for effect in state.timed_effects
                if effect.effect_id not in ended and effect.source_effect_id not in ended
            ]
        return ended
    except Exception as exc:
        logger.exception("Failed full-HP self-buff cleanup for %s.", state.template.name)
        raise RuntimeError("Self-buff HP lifecycle could not be evaluated.") from exc
