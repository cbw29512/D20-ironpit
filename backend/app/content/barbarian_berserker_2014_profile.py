from __future__ import annotations

import logging

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _audit(feature_id: str, feature_name: str, category: str, *, source: str,
           weapon_id: str | None = None) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id, feature_name=feature_name, source_reference=source,
        category=category, combat_relevant=True, automated=True, runtime_attack_weapon_id=weapon_id,
    )


def _base_scores() -> AbilityScores:
    return AbilityScores(strength=15, dexterity=13, constitution=14,
                         intelligence=8, wisdom=12, charisma=10)


def _species_increases() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=1) for ability in _ABILITIES]


def _advancements(level: int) -> list[AbilityIncrease]:
    increases: list[AbilityIncrease] = []
    if level >= 4:
        increases.append(AbilityIncrease(ability="strength", amount=2))
    if level >= 8:
        increases.append(AbilityIncrease(ability="strength", amount=2))
    return increases


def _final_scores(base: AbilityScores, species: list[AbilityIncrease],
                  advancements: list[AbilityIncrease]) -> AbilityScores:
    values = base.model_dump()
    for increase in [*species, *advancements]:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _feature_audits(level: int) -> list[FeatureAudit]:
    barbarian = "D&D Basic Rules 2014: Barbarian"
    berserker = "D&D Basic Rules 2014: Path of the Berserker"
    audits = [
        _audit("human-ability-increase", "Human Ability Score Increase", "species",
               source="D&D Basic Rules 2014: Human"),
        _audit("rage", "Rage", "class", source=barbarian),
        _audit("unarmored-defense", "Unarmored Defense", "class", source=barbarian),
        _audit("greataxe", "Greataxe", "equipment", source="D&D Basic Rules 2014: Equipment",
               weapon_id="greataxe"),
        _audit("handaxe", "Handaxe", "equipment", source="D&D Basic Rules 2014: Equipment",
               weapon_id="handaxe"),
        _audit("soldier-athletics", "Soldier Athletics Proficiency", "background",
               source="D&D Basic Rules 2014: Soldier"),
    ]
    if level >= 2:
        audits.extend([
            _audit("reckless-attack", "Reckless Attack", "class", source=barbarian),
            _audit("danger-sense", "Danger Sense", "class", source=barbarian),
        ])
    if level >= 3:
        audits.append(_audit("frenzy", "Frenzy", "subclass", source=berserker))
    if level >= 5:
        audits.extend([
            _audit("extra-attack", "Extra Attack", "class", source=barbarian),
            _audit("fast-movement", "Fast Movement", "class", source=barbarian),
        ])
    if level >= 6:
        audits.append(_audit("mindless-rage", "Mindless Rage", "subclass", source=berserker))
    if level >= 7:
        audits.append(_audit("feral-instinct", "Feral Instinct", "class", source=barbarian))
    if level >= 9:
        audits.append(_audit("brutal-critical", "Brutal Critical", "class", source=barbarian))
    if level >= 10:
        audits.append(_audit("intimidating-presence", "Intimidating Presence", "subclass", source=berserker))
    return audits


def build_rokhan_stonefury_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Rokhan profile certification covers levels 1 through 10.")
        base = _base_scores(); species = _species_increases(); advancements = _advancements(level)
        return CharacterBuildProfile(
            id=f"build-rokhan-stonefury-2014-l{level}", template_id=f"rokhan-stonefury-2014-l{level}",
            character_name="Rokhan Stonefury", class_id="barbarian", class_name="Barbarian", level=level,
            ruleset="2014", subclass_id="path-berserker" if level >= 3 else None,
            subclass_name="Path of the Berserker" if level >= 3 else None, build_id="berserker-greataxe",
            species_id="human", species_name="Human", background_id="soldier", background_name="Soldier",
            base_ability_scores=base, species_increases=species, advancement_increases=advancements,
            final_ability_scores=_final_scores(base, species, advancements), class_equipment_option="package",
            class_equipment=["Greataxe", "Two Handaxes", "Explorer's Pack", "Four Javelins"],
            background_equipment_option="package",
            background_equipment=["Rank Insignia", "Trophy", "Gaming Set", "Common Clothes", "10 gp"],
            skill_proficiencies=["Athletics", "Intimidation", "Perception", "Survival"],
            weapon_masteries=[], combat_loadout_kind="two-handed", feature_audits=_feature_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Human", "D&D Basic Rules 2014: Barbarian",
                "D&D Basic Rules 2014: Path of the Berserker", "D&D Basic Rules 2014: Soldier",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rokhan build profile at level %s", level)
        raise
