from __future__ import annotations

import logging

from app.content.bard_lore_2014_audits import build_bard_lore_2014_feature_audits
from app.content.bard_lore_2014_data import ASI_CHOICES, BASE_SCORES, HALF_ELF_INCREASES, ability_scores
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def _species_increases() -> list[AbilityIncrease]:
    try:
        return [
            AbilityIncrease(ability=ability, amount=amount)
            for ability, amount in HALF_ELF_INCREASES.items()
        ]
    except Exception:
        logger.exception("Failed to compile Lyra's Half-Elf increases")
        raise


def _advancements(level: int) -> list[AbilityIncrease]:
    try:
        return [
            AbilityIncrease(ability=ability, amount=amount)
            for required, ability, amount in ASI_CHOICES
            if level >= required
        ]
    except Exception:
        logger.exception("Failed to compile Lyra's advancements at level %s", level)
        raise


def _skills(level: int) -> list[str]:
    skills = ["Acrobatics", "Deception", "History", "Insight", "Perception", "Performance", "Persuasion"]
    if level >= 3:
        skills.extend(["Arcana", "Investigation", "Medicine"])
    return skills


def build_lyra_silverstring_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lyra profile covers levels 1 through 20.")
        return CharacterBuildProfile(
            id=f"build-lyra-silverstring-2014-l{level}",
            template_id=f"lyra-silverstring-2014-l{level}",
            character_name="Lyra Silverstring",
            class_id="bard",
            class_name="Bard",
            level=level,
            ruleset="2014",
            subclass_id="college-lore" if level >= 3 else None,
            subclass_name="College of Lore" if level >= 3 else None,
            build_id="lore-support-caster",
            species_id="half-elf",
            species_name="Half-Elf",
            background_id="noble",
            background_name="Noble",
            base_ability_scores=BASE_SCORES,
            species_increases=_species_increases(),
            advancement_increases=_advancements(level),
            final_ability_scores=ability_scores(level),
            class_equipment_option="package",
            class_equipment=["Rapier", "Entertainer's Pack", "Lute", "Leather Armor", "Dagger"],
            background_equipment_option="package",
            background_equipment=[
                "Fine Clothes", "Signet Ring", "Scroll of Pedigree", "Purse", "25 gp",
            ],
            skill_proficiencies=_skills(level),
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_bard_lore_2014_feature_audits(level),
            source_references=[
                "D&D SRD 5.1 (2014): Half-Elf",
                "D&D SRD 5.1 (2014): Bard",
                "D&D SRD 5.1 (2014): College of Lore",
                "D&D Basic Rules 2014: Noble and Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Lyra Silverstring profile at level %s", level)
        raise
