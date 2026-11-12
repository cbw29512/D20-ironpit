"""One source-neutral understood-spoken-language gate for spoken effects.

An empty source or target language inventory means compatibility is unknown:
the effect is not eligible until a source-backed positive relationship exists.
"""
from __future__ import annotations

import logging

from app.domain.combatants import CombatantTemplate

logger = logging.getLogger(__name__)


def target_understands_caster_language(
    caster: CombatantTemplate, target: CombatantTemplate,
) -> bool:
    try:
        spoken = {str(value).casefold() for value in caster.spoken_languages}
        understood = {str(value).casefold() for value in target.understood_languages}
        if not spoken or not understood:
            return False
        return "all" in spoken or "all" in understood or bool(spoken & understood)
    except Exception:
        logger.exception(
            "Shared spoken-language eligibility failed for %s and %s.",
            caster.id, target.id,
        )
        raise
