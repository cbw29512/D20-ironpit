from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.ranger_hunter_2024_audits import build_ranger_2024_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_rowan_ashtrail_2024_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Rowan profile currently certifies levels 1 through 20.")
        hero = HERO_BY_CLASS["ranger"]
        base = canonical_base_ability_scores("ranger")
        allowed = ["dexterity", "wisdom", "constitution"]
        background = canonical_background_increases("ranger", allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="dexterity", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="dexterity", amount=1),
                AbilityIncrease(ability="wisdom", amount=1),
            ])
        if level >= 12:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 16:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 19:
            advancement.append(AbilityIncrease(ability="dexterity", amount=1))
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = AbilityScores(**values)
        return CharacterBuildProfile(
            id=f"build-rowan-ashtrail-2024-l{level}",
            template_id=canonical_template_id("ranger", level),
            character_name=hero.hero_name,
            class_id="ranger",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            build_id="archer",
            subclass_id="hunter" if level >= 3 else None,
            subclass_name="Hunter" if level >= 3 else None,
            species_id="wood-elf",
            species_name="Wood Elf",
            background_id="outlander",
            background_name="Outlander",
            origin_feat_id="alert",
            origin_feat_name="Alert",
            base_ability_scores=base,
            background_allowed_abilities=allowed,
            background_increases=background,
            advancement_increases=advancement,
            final_ability_scores=final,
            ability_score_maximums={"dexterity": 30} if level >= 19 else {},
            class_equipment_option="package",
            class_equipment=[
                "Studded Leather Armor", "Scimitar", "Shortsword", "Longbow",
                "20 Arrows", "Quiver", "Druidic Focus", "Explorer's Pack", "7 GP",
            ],
            background_equipment_option="package",
            background_equipment=["Staff", "Hunting Trap", "Traveler's Clothes", "10 GP"],
            skill_proficiencies=[
                "Athletics", "Survival", "Perception", "Stealth", "Insight", "Investigation",
            ],
            weapon_masteries=["longbow", "shortsword"],
            fighting_style="Archery" if level >= 2 else None,
            fighting_styles=["Archery"] if level >= 2 else [],
            combat_loadout_kind="dual-wield",
            feature_audits=build_ranger_2024_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Ranger",
                "D&D Beyond Basic Rules 2024: Hunter",
                "D&D Beyond Basic Rules 2024: Elf — Wood Elf",
                "D&D Beyond Basic Rules 2024: Alert",
                "D&D Beyond Basic Rules 2024: Backgrounds and Species from Older Books",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Rowan Ashtrail profile at level %s.", level)
        raise
