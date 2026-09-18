from __future__ import annotations

import logging

from app.content.paladin_devotion_2014_audits import build_paladin_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _base() -> AbilityScores:
    return AbilityScores(
        strength=15,
        dexterity=10,
        constitution=13,
        intelligence=8,
        wisdom=12,
        charisma=14,
    )


def _species() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=1) for ability in _ABILITIES]


def _advancements(level: int) -> list[AbilityIncrease]:
    milestones = ((4, "strength", 2), (8, "charisma", 2))
    return [
        AbilityIncrease(ability=ability, amount=amount)
        for required, ability, amount in milestones
        if level >= required
    ]


def _final(
    base: AbilityScores,
    species: list[AbilityIncrease],
    advances: list[AbilityIncrease],
) -> AbilityScores:
    values = base.model_dump()
    for increase in [*species, *advances]:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def build_aurelia_brightshield_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Aurelia profile covers levels 1 through 10.")
        base = _base()
        species = _species()
        advances = _advancements(level)
        return CharacterBuildProfile(
            id=f"build-aurelia-brightshield-2014-l{level}",
            template_id=f"aurelia-brightshield-2014-l{level}",
            character_name="Aurelia Brightshield",
            class_id="paladin",
            class_name="Paladin",
            level=level,
            ruleset="2014",
            subclass_id="oath-devotion" if level >= 3 else None,
            subclass_name="Oath of Devotion" if level >= 3 else None,
            build_id="devotion-sword-shield",
            species_id="human",
            species_name="Human",
            background_id="noble",
            background_name="Noble",
            base_ability_scores=base,
            species_increases=species,
            advancement_increases=advances,
            final_ability_scores=_final(base, species, advances),
            class_equipment_option="package",
            class_equipment=[
                "Longsword",
                "Shield",
                "5 Javelins",
                "Priest's Pack",
                "Chain Mail",
                "Holy Symbol",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Fine Clothes",
                "Signet Ring",
                "Scroll of Pedigree",
                "Purse",
                "25 gp",
            ],
            skill_proficiencies=["Athletics", "Insight", "History", "Persuasion"],
            weapon_masteries=[],
            fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [],
            combat_loadout_kind="one-hander-shield",
            feature_audits=build_paladin_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human, Noble, Equipment",
                "D&D SRD 5.1 (2014): Paladin",
                "D&D SRD 5.1 (2014): Oath of Devotion",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Aurelia Brightshield profile at level %s", level)
        raise
