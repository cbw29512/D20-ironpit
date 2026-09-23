from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def can_see(observer: CombatantState, target: CombatantState, distance_ft: int) -> bool:
    """Return whether one combatant can satisfy a rule that requires seeing another."""
    try:
        if distance_ft < 0:
            raise ValueError("Visibility distance cannot be negative.")
        senses = observer.template.senses
        blindsight_available = (
            senses.blindsight_ft > 0
            and distance_ft <= senses.blindsight_ft
            and not (
                senses.blindsight_requires_hearing
                and has_condition(observer, "deafened")
            )
        )
        if blindsight_available:
            return True
        if has_condition(observer, "blinded"):
            return False
        if senses.blind_beyond_ft is not None and distance_ft > senses.blind_beyond_ft:
            return False
        if has_condition(target, "invisible"):
            return senses.truesight_ft > 0 and distance_ft <= senses.truesight_ft
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Visibility resolution failed for %s -> %s.",
            observer.template.name,
            target.template.name,
        )
        raise RuntimeError("Combat visibility could not be resolved.") from exc
