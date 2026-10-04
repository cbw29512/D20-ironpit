from __future__ import annotations

import logging
from dataclasses import replace

from app.content.pregen_combat_profiles import PregenCombatProfile
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def untrained_grapple_escape_bonuses(
    scores: AbilityScores,
    existing: dict[str, int],
) -> dict[str, int]:
    """Supply untrained Athletics/Acrobatics so Grappled creatures can attempt the printed check."""
    try:
        added: dict[str, int] = {}
        if "athletics" not in existing:
            added["athletics"] = scores.modifier("strength")
        if "acrobatics" not in existing:
            added["acrobatics"] = scores.modifier("dexterity")
        return added
    except Exception:
        logger.exception("Failed to derive untrained Athletics/Acrobatics bonuses.")
        raise


def complete_template_grapple_escape_skills(template: CombatantTemplate) -> CombatantTemplate:
    try:
        if template.ability_scores is None:
            return template
        added = untrained_grapple_escape_bonuses(template.ability_scores, template.skill_bonuses)
        if not added:
            return template
        return template.model_copy(update={"skill_bonuses": {**template.skill_bonuses, **added}})
    except Exception:
        logger.exception("Failed to complete grapple-escape skills for %s.", template.id)
        raise


def complete_profile_grapple_escape_skills(profile: PregenCombatProfile) -> PregenCombatProfile:
    try:
        existing = dict(profile.skill_bonuses)
        added = untrained_grapple_escape_bonuses(profile.abilities, existing)
        if not added:
            return profile
        return replace(profile, skill_bonuses=(*profile.skill_bonuses, *added.items()))
    except Exception:
        logger.exception("Failed to complete grapple-escape fingerprint for %s.", profile.template_id)
        raise


def complete_profile_map(
    profiles: dict[str, PregenCombatProfile],
) -> dict[str, PregenCombatProfile]:
    try:
        return {
            template_id: complete_profile_grapple_escape_skills(profile)
            for template_id, profile in profiles.items()
        }
    except Exception:
        logger.exception("Failed to complete grapple-escape combat fingerprints.")
        raise
