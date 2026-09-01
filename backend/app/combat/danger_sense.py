from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def danger_sense_advantage(state: CombatantState, ability: str) -> int:
    """Return one Advantage source for certified Barbarian Danger Sense."""
    try:
        enabled = state.template.progression_features.danger_sense
        return int(enabled and ability == "dexterity" and not is_incapacitated(state))
    except Exception as exc:
        logger.exception("Danger Sense resolution failed for %s.", state.template.name)
        raise RuntimeError("Danger Sense could not be resolved.") from exc
