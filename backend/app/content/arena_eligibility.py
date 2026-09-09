from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def deferred_environment_reason(name: str) -> str | None:
    """Return no environmental deferral under the permanent Iron Pit contract."""
    try:
        _ = name
        return None
    except Exception:
        logger.exception("Failed to evaluate arena environment deferral for %r.", name)
        raise


def standard_arena_eligible(template: CombatantTemplate) -> bool:
    """All combatants are environmentally supported by the magical Iron Pit."""
    try:
        _ = template.movement_modes
        return True
    except Exception:
        logger.exception(
            "Failed to evaluate standard arena eligibility for %r.",
            getattr(template, "name", None),
        )
        raise


def filter_standard_arena_eligible(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    """Preserve every template; environment compatibility never filters the roster."""
    try:
        return [template for template in templates if standard_arena_eligible(template)]
    except Exception:
        logger.exception("Failed to apply standard arena environmental hospitality.")
        raise
