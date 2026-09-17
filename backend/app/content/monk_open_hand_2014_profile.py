from __future__ import annotations

import logging

from app.content.monk_open_hand_2014_audits import build_monk_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)
_ABILITIES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)


def _base() -> AbilityScores:
    return AbilityScores(
        strength=12,
        dexterity=15,
        constitution=13,
        intelligence=10,
        wisdom=14,
        charisma=8,
    )


def _species() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=1) for ability in _ABILITIES]


def _advancements(level: int) -> list[AbilityIncrease]:
    milestones = ((4, "dexterity", 2), (8, "dexterity", 2))
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


def build_kael_stillwater_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Kael profile covers levels 1 through 10.")
        base = _base()
        species = _species()
        advances = _advancements(level)
        return CharacterBuildProfile(
            id=f"build-kael-stillwater-2014-l{level}",
            template_id=f"kael-stillwater-2014-l{level}",
            character_name="Kael Stillwater",
            class_id="monk",
            class_name="Monk",
            level=level,
            ruleset="2014",
            subclass_id="way-open-hand" if level >= 3 else None,
            subclass_name="Way of the Open Hand" if level >= 3 else None,
            build_id="open-hand-unarmed",
            species_id="human",
            species_name="Human",
            background_id="acolyte",
            background_name="Acolyte",
            base_ability_scores=base,
            species_increases=species,
            advancement_increases=advances,
            final_ability_scores=_final(base, species, advances),
            class_equipment_option="package",
            class_equipment=["Shortsword", "Explorer's Pack", "10 Darts"],
            background_equipment_option="package",
            background_equipment=[
                "Holy Symbol",
                "Prayer Book",
                "5 Sticks of Incense",
                "Vestments",
                "Common Clothes",
                "Pouch",
                "15 gp",
            ],
            skill_proficiencies=["Acrobatics", "Stealth", "Insight", "Religion"],
            weapon_masteries=[],
            combat_loadout_kind="unarmed",
            feature_audits=build_monk_2014_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human",
                "D&D SRD 5.1 (2014): Monk",
                "D&D SRD 5.1 (2014): Way of the Open Hand",
                "D&D Basic Rules 2014: Acolyte",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Kael Stillwater profile at level %s", level)
        raise
