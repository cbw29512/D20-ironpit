from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def complete_template_grapple_escape_skills(
    template: CombatantTemplate,
) -> CombatantTemplate:
    """Supply untrained Athletics/Acrobatics from immutable ability scores."""
    try:
        if template.ability_scores is None:
            return template
        added: dict[str, int] = {}
        if "athletics" not in template.skill_bonuses:
            added["athletics"] = template.ability_scores.modifier("strength")
        if "acrobatics" not in template.skill_bonuses:
            added["acrobatics"] = template.ability_scores.modifier("dexterity")
        if not added:
            return template
        return template.model_copy(update={
            "skill_bonuses": {**template.skill_bonuses, **added},
        })
    except Exception:
        logger.exception("Failed to complete grapple-escape skills for %s.", template.id)
        raise
