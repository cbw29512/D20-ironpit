from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.wizard_evoker_2024_audits import build_elian_evoker_2024_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_elian_starweaver_2024_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Elian profile currently certifies levels 1 through 20.")
        hero = HERO_BY_CLASS["wizard"]
        base = canonical_base_ability_scores("wizard")
        background_allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("wizard", background_allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="intelligence", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="intelligence", amount=1),
                AbilityIncrease(ability="wisdom", amount=1),
            ])
        if level >= 12:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 16:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 19:
            advancement.append(AbilityIncrease(ability="charisma", amount=1))
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = AbilityScores(**values)
        return CharacterBuildProfile(
            id=f"build-elian-starweaver-2024-l{level}",
            template_id=canonical_template_id("wizard", level),
            character_name=hero.hero_name,
            class_id="wizard",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            subclass_id="evoker" if level >= 3 else None,
            subclass_name="Evoker" if level >= 3 else None,
            build_id="fire-damage",
            species_id="human",
            species_name="Human",
            background_id="sage",
            background_name="Sage",
            origin_feat_id="magic-initiate-wizard",
            origin_feat_name="Magic Initiate (Wizard)",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            advancement_increases=advancement,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=["Dagger", "Dagger", "Arcane Focus", "Scholar's Pack", "Spellbook"],
            background_equipment_option="package",
            background_equipment=["Calligrapher's Supplies", "Book", "Parchment", "Robe", "8 GP"],
            skill_proficiencies=[
                "Arcana", "History", "Investigation", "Insight",
                "Religion", "Medicine", "Nature", "Perception",
            ],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_elian_evoker_2024_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Wizard",
                "D&D Beyond Basic Rules 2024: Evoker",
                "D&D Beyond Basic Rules 2024: Human",
                "D&D Beyond Basic Rules 2024: Sage",
                "D&D Beyond Basic Rules 2024: Fire Bolt; Burning Hands; Magic Missile",
                "D&D Beyond Basic Rules 2024: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Elian Starweaver profile at level %s.", level)
        raise
