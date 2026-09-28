from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def rage_max_rounds(state: CombatantState) -> int:
    try:
        return 10 if state.template.ruleset == "2014" else 100
    except Exception:
        logger.exception("Failed to resolve Rage maximum duration.")
        raise


def rage_persists_without_maintenance(state: CombatantState) -> bool:
    try:
        features = state.template.progression_features
        return (
            features.rage_persists_without_maintenance
            or (state.template.ruleset == "2014" and features.persistent_rage_2014)
        )
    except Exception:
        logger.exception("Failed to resolve Rage persistence policy.")
        raise


def rage_ends_for_state(state: CombatantState) -> bool:
    try:
        if rage_persists_without_maintenance(state):
            return (
                state.is_dead
                or state.is_unconscious
                or (state.template.ruleset == "2024" and state.template.wearing_heavy_armor)
            )
        return state.template.wearing_heavy_armor or state.is_dead or is_incapacitated(state)
    except Exception:
        logger.exception("Failed to resolve Rage early-ending policy.")
        raise
