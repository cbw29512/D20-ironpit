from __future__ import annotations

import logging

from app.domain.character_builds import (
    AbilityIncrease,
    AbilityScores,
    CharacterBuildProfile,
    FeatureAudit,
)

logger = logging.getLogger(__name__)
_ABILITIES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)


def _audit(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool = True,
    automated: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    source = (
        "D&D SRD 5.1 (2014): Way of the Open Hand"
        if category == "subclass"
        else "D&D SRD 5.1 (2014): Monk"
    )
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference=source,
        category=category,
        combat_relevant=combat,
        automated=automated,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
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


def _audits(level: int) -> list[FeatureAudit]:
    audits = [
        _audit(
            "human-ability-increase",
            "Human Ability Score Increase",
            "species",
            combat=False,
            automated=False,
        ),
        _audit("unarmored-defense", "Unarmored Defense", "class"),
        _audit("martial-arts", "Martial Arts", "class"),
        _audit("shortsword", "Shortsword", "equipment", weapon_id="shortsword"),
    ]
    if level >= 2:
        audits.extend(
            [
                _audit("ki", "Ki", "class"),
                _audit("flurry-of-blows", "Flurry of Blows", "class"),
                _audit("patient-defense", "Patient Defense", "class"),
                _audit("step-of-the-wind", "Step of the Wind", "class"),
                _audit("unarmored-movement", "Unarmored Movement", "class"),
            ]
        )
    if level >= 3:
        audits.extend(
            [
                _audit("deflect-missiles", "Deflect Missiles", "class"),
                _audit("open-hand-technique", "Open Hand Technique", "subclass"),
            ]
        )
    if level >= 4:
        audits.append(
            _audit(
                "slow-fall",
                "Slow Fall",
                "class",
                combat=False,
                automated=False,
                notes="The standard Iron Pit arena has no falling hazard.",
            )
        )
    if level >= 5:
        audits.extend(
            [
                _audit("extra-attack", "Extra Attack", "class"),
                _audit("stunning-strike", "Stunning Strike", "class"),
            ]
        )
    if level >= 6:
        audits.extend(
            [
                _audit(
                    "ki-empowered-strikes",
                    "Ki-Empowered Strikes",
                    "class",
                    notes=(
                        "The arena physical-damage pipeline does not separate magical from "
                        "nonmagical B/P/S, so the unarmed strike is already resolved correctly."
                    ),
                ),
                _audit("wholeness-of-body", "Wholeness of Body", "subclass"),
            ]
        )
    if level >= 7:
        audits.extend(
            [
                _audit("evasion", "Evasion", "class"),
                _audit("stillness-of-mind", "Stillness of Mind", "class"),
            ]
        )
    if level >= 10:
        audits.append(_audit("purity-of-body", "Purity of Body", "class"))
    return audits


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
            class_equipment=[
                "Shortsword",
                "Explorer's Pack",
                "10 Darts",
            ],
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
            combat_loadout_kind="unarmed-offense",
            feature_audits=_audits(level),
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
