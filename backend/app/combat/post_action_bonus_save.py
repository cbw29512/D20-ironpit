"""Generic legal post-Action Bonus Action save selection.

A fresh target may become eligible only after a regular Action. Reuse the
same source-parameterized save scheduler used in the pre-Action window.
"""
from __future__ import annotations

import logging

from app.combat.bonus_save_actions import resolve_bonus_save_action
from app.combat.condition_rules import is_incapacitated

logger = logging.getLogger(__name__)


def resolve_post_action_bonus_save(sequence, round_number, actor, setup, dice):
    """Resolve any still-legal Bonus Action save after the main Action."""
    try:
        state = actor.state
        if (
            not state.is_alive
            or state.is_dead
            or state.current_hp <= 0
            or is_incapacitated(state)
            or not state.bonus_action_available
        ):
            return [], sequence
        return resolve_bonus_save_action(
            sequence, round_number, actor, setup, dice,
        )
    except Exception:
        logger.exception(
            "Failed post-Action Bonus Action save selection for %s.",
            actor.combatant_id,
        )
        raise
