from __future__ import annotations

import logging

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, source: str, *, weapon_id: str | None = None, notes: str | None = None) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference=source,
        category=category,
        combat_relevant=True,
        automated=True,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
    )


def _base_scores() -> AbilityScores:
    return AbilityScores(strength=15, dexterity=14, constitution=13, intelligence=8, wisdom=12, charisma=10)


def _species_increases() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability="strength", amount=2), AbilityIncrease(ability="constitution", amount=1)]


def _advancements(level: int) -> list[AbilityIncrease]:
    increases: list[AbilityIncrease] = []
    if level >= 4:
        increases.extend([AbilityIncrease(ability="strength", amount=1), AbilityIncrease(ability="constitution", amount=1)])
    if level >= 8:
        increases.append(AbilityIncrease(ability="strength", amount=2))
    return increases


def _final_scores(base: AbilityScores, species: list[AbilityIncrease], advances: list[AbilityIncrease]) -> AbilityScores:
    values = base.model_dump()
    for increase in [*species, *advances]:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _audits(level: int) -> list[FeatureAudit]:
    barbarian = "D&D Basic Rules 2014: Barbarian"
    berserker = "D&D Basic Rules 2014: Path of the Berserker"
    half_orc = "D&D Basic Rules 2014: Half-Orc"
    audits = [
        _audit("half-orc-ability-increase", "Half-Orc Ability Score Increase", "species", half_orc),
        _audit("relentless-endurance", "Relentless Endurance", "species", half_orc),
        _audit("savage-attacks", "Savage Attacks", "species", half_orc),
        _audit("rage", "Rage", "class", barbarian),
        _audit("unarmored-defense", "Unarmored Defense", "class", barbarian),
        _audit("greataxe", "Greataxe", "equipment", "D&D Basic Rules 2014: Equipment", weapon_id="greataxe"),
        _audit("handaxe", "Handaxe", "equipment", "D&D Basic Rules 2014: Equipment", weapon_id="handaxe"),
        _audit("soldier-athletics", "Soldier Athletics Proficiency", "background", "D&D Basic Rules 2014: Soldier"),
    ]
    if level >= 2:
        audits.extend([_audit("reckless-attack", "Reckless Attack", "class", barbarian), _audit("danger-sense", "Danger Sense", "class", barbarian)])
    if level >= 3:
        audits.append(_audit("frenzy-2014", "Frenzy", "subclass", berserker))
    if level >= 5:
        audits.extend([_audit("extra-attack", "Extra Attack", "class", barbarian), _audit("fast-movement", "Fast Movement", "class", barbarian)])
    if level >= 6:
        audits.append(_audit("mindless-rage", "Mindless Rage", "subclass", berserker))
    if level >= 7:
        audits.append(_audit("feral-instinct", "Feral Instinct", "class", barbarian, notes="Iron Pit starts combat with both sides aware; initiative Advantage is automated."))
    if level >= 9:
        audits.append(_audit("brutal-critical", "Brutal Critical", "class", barbarian))
    if level >= 10:
        audits.append(_audit("intimidating-presence", "Intimidating Presence", "subclass", berserker))
    return audits


def build_rokhan_stonefury_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Rokhan profile certification currently covers levels 1 through 10.")
        base = _base_scores(); species = _species_increases(); advances = _advancements(level)
        return CharacterBuildProfile(
            id=f"build-rokhan-stonefury-2014-l{level}",
            template_id=f"rokhan-stonefury-2014-l{level}",
            character_name="Rokhan Stonefury", class_id="barbarian", class_name="Barbarian", level=level,
            ruleset="2014", subclass_id="berserker" if level >= 3 else None,
            subclass_name="Path of the Berserker" if level >= 3 else None, build_id="berserker-greataxe",
            species_id="half-orc", species_name="Half-Orc", background_id="soldier", background_name="Soldier",
            base_ability_scores=base, species_increases=species, advancement_increases=advances,
            final_ability_scores=_final_scores(base, species, advances),
            class_equipment_option="package",
            class_equipment=["Greataxe", "Two Handaxes", "Explorer's Pack", "Four Javelins"],
            background_equipment_option="package",
            background_equipment=["Rank Insignia", "Trophy", "Gaming Set", "Common Clothes", "10 gp"],
            skill_proficiencies=["Athletics", "Intimidation", "Animal Handling", "Perception", "Survival"],
            weapon_masteries=[], combat_loadout_kind="two-handed", feature_audits=_audits(level),
            source_references=[
                "D&D Basic Rules 2014: Half-Orc", "D&D Basic Rules 2014: Barbarian",
                "D&D Basic Rules 2014: Path of the Berserker", "D&D Basic Rules 2014: Soldier",
                "D&D Basic Rules 2014: Equipment", "D&D Basic Rules 2014: Proficiencies",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rokhan build profile at level %s", level)
        raise
