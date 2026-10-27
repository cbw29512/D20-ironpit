from __future__ import annotations

import logging

from app.domain.environment_contexts import EnvironmentContextReaction

logger = logging.getLogger(__name__)


def sunlight_sensitivity_2014() -> EnvironmentContextReaction:
    """2014 printed Sunlight Sensitivity: attack rolls and sight-based Perception."""
    try:
        return EnvironmentContextReaction(
            source_id="sunlight-sensitivity",
            source_name="Sunlight Sensitivity",
            context_id="sunlight",
            disadvantage_on=["attack_rolls", "sight_based_perception_checks"],
        )
    except Exception:
        logger.exception("Failed to build 2014 Sunlight Sensitivity context reaction.")
        raise


def verified_sunlight_weakness_2014(monster) -> bool:
    """Source proof for an always-owned trait, never an arena-neutral exemption."""
    try:
        from app.content.monster_source_sections_2014 import source_sections_2014

        if "Sunlight Weakness" not in monster.trait_names:
            return False
        clause = source_sections_2014(monster.source_traits).get(
            "Sunlight Weakness", "",
        ).casefold()
        return all(phrase in clause for phrase in (
            "while in sunlight", "disadvantage on attack rolls",
            "ability checks", "saving throws",
        ))
    except Exception:
        logger.exception("Sunlight Weakness source proof failed for %s.", monster.name)
        raise


def sunlight_weakness_2014() -> EnvironmentContextReaction:
    """The permanent printed weakness responds to live sunlight only."""
    return EnvironmentContextReaction(
        source_id="sunlight-weakness",
        source_name="Sunlight Weakness",
        context_id="sunlight",
        disadvantage_on=["attack_rolls", "ability_checks", "saving_throws"],
    )


def bright_light_sensitivity_2014() -> EnvironmentContextReaction:
    """2014 printed Light Sensitivity: attack rolls and sight-based Perception in bright light."""
    try:
        return EnvironmentContextReaction(
            source_id="bright-light-sensitivity",
            source_name="Light Sensitivity",
            context_id="bright_light",
            disadvantage_on=["attack_rolls", "sight_based_perception_checks"],
        )
    except Exception:
        logger.exception("Failed to build 2014 Light Sensitivity context reaction.")
        raise


def verified_bright_light_sensitivity_2014(monster) -> bool:
    """Source proof for printed bright-light disadvantage on attacks and sight Perception."""
    try:
        from app.content.monster_source_sections_2014 import source_sections_2014

        if "Light Sensitivity" not in monster.trait_names:
            return False
        clause = source_sections_2014(monster.source_traits).get(
            "Light Sensitivity", "",
        ).casefold()
        return all(phrase in clause for phrase in (
            "while in bright light", "disadvantage on attack rolls",
            "wisdom (perception) checks that rely on sight",
        ))
    except Exception:
        logger.exception("Light Sensitivity source proof failed for %s.", monster.name)
        raise
