from __future__ import annotations

import logging

from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def attack_roll_disadvantage_sources(state: CombatantState) -> int:
    try:
        return sum(
            1 for item in state.active_modifiers
            if item.kind is ModifierKind.ATTACK_ROLL_DISADVANTAGE
        )
    except Exception:
        logger.exception("Failed attack-roll Disadvantage lookup for %s.", state.template.id)
        raise


def ability_check_disadvantage_sources(state: CombatantState) -> int:
    try:
        return sum(
            1 for item in state.active_modifiers
            if item.kind is ModifierKind.ABILITY_CHECK_DISADVANTAGE
        )
    except Exception:
        logger.exception("Failed ability-check Disadvantage lookup for %s.", state.template.id)
        raise
