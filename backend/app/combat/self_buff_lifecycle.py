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
            # Source-owned cleanup must restore any fight-local size override,
            # curses and modifiers instead of discarding the timed record.
            from app.combat.timed_condition_lifecycle import remove_effect_group
            for effect in list(state.timed_effects):
                if effect not in state.timed_effects:
                    continue
                if effect.effect_id in ended or effect.source_effect_id in ended:
                    remove_effect_group(state, effect)
            # Some source-defined modes (e.g. Berserk) have an active sentinel
            # even when no timed group remains. Clear only the ended mode.
            state.active_effect_ids = [
                effect_id for effect_id in state.active_effect_ids
                if effect_id not in ended
            ]
        return ended
    except Exception as exc:
        logger.exception("Failed full-HP self-buff cleanup for %s.", state.template.name)
        raise RuntimeError("Self-buff HP lifecycle could not be evaluated.") from exc
