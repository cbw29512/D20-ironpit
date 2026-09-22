from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_defender_advantage_suppression(
    defender: CombatantState,
    advantage_sources: int,
) -> int:
    """Suppress attack-roll Advantage sources when defender data forbids Advantage."""
    try:
        features = defender.template.progression_features
        if features.suppress_attack_advantage_while_not_incapacitated and not is_incapacitated(defender):
            return 0
        return advantage_sources
    except Exception as exc:
        logger.exception("Failed to resolve defender attack-Advantage suppression.")
        raise RuntimeError("Defender attack-Advantage suppression failed.") from exc
