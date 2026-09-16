from __future__ import annotations

import logging

from app.content.fighter_2014 import karnok_2014_template_id
from app.content.fighter_2014_combat_levels import fighter_2014_level
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _audit(feature_id: str, name: str, category: str, *, weapon: str | None = None,
           notes: str | None = None) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2014",
        category=category,
        combat_relevant=True,
        automated=True,
        runtime_attack_weapon_id=weapon,
        notes=notes,
    )


def _species_increases() -> list[AbilityIncrease]:
    return [
        AbilityIncrease(ability=ability, amount=1)
        for ability in ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
    ]


def _advancement_increases(level: int) -> list[AbilityIncrease]:
    increases: list[AbilityIncrease] = []
    if level >= 4:
        increases.append(AbilityIncrease(ability="strength", amount=2))
    if level >= 6:
        increases.append(AbilityIncrease(ability="strength", amount=2))
    if level >= 8:
        increases.append(AbilityIncrease(ability="constitution", amount=2))
    return increases


def _features(level: int) -> list[FeatureAudit]:
    features = [
        _audit("human-ability-increases", "Human Ability Score Increase", "species"),
        _audit("fighting-style-defense", "Defense", "class"),
        _audit("second-wind", "Second Wind", "class"),
        _audit("greatsword", "Greatsword", "equipment", weapon="greatsword"),
        _audit("light-crossbow", "Light Crossbow", "equipment", weapon="light-crossbow"),
    ]
    if level >= 2:
        features.append(_audit("action-surge", "Action Surge", "class"))
    if level >= 3:
        features.append(_audit("improved-critical", "Improved Critical", "subclass"))
    if level >= 4:
        features.append(_audit("ability-score-improvement-4", "Ability Score Improvement", "class"))
    if level >= 5:
        features.append(_audit("extra-attack", "Extra Attack", "class"))
    if level >= 6:
        features.append(_audit("ability-score-improvement-6", "Ability Score Improvement", "class"))
    if level >= 7:
        features.append(_audit(
            "remarkable-athlete", "Remarkable Athlete", "subclass",
            notes="Half proficiency is automated for unproficient STR/DEX/CON checks used by the arena; jump distance is arena-neutral.",
        ))
    if level >= 8:
        features.append(_audit("ability-score-improvement-8", "Ability Score Improvement", "class"))
    if level >= 9:
        features.append(_audit("indomitable", "Indomitable", "class"))
    if level >= 10:
        features.append(_audit("additional-fighting-style-archery", "Archery", "subclass"))
    return features


def build_karnok_stoneward_2014_profile(level: int) -> CharacterBuildProfile:
    """Build the legal 2014 Human Champion Fighter profile used by the certified runtime template."""
    try:
        row = fighter_2014_level(level)
        return CharacterBuildProfile(
            id=f"build-karnok-stoneward-2014-l{level}",
            template_id=karnok_2014_template_id(level),
            character_name="Karnok Stoneward",
            class_id="fighter",
            class_name="Fighter",
            level=level,
            ruleset="2014",
            subclass_id="champion" if level >= 3 else None,
            subclass_name="Champion" if level >= 3 else None,
            build_id="canonical-2014",
            species_id="human",
            species_name="Human",
            background_id="soldier",
            background_name="Soldier",
            base_ability_scores=AbilityScores(
                strength=15, dexterity=13, constitution=15,
                intelligence=10, wisdom=10, charisma=8,
            ),
            species_increases=_species_increases(),
            advancement_increases=_advancement_increases(level),
            final_ability_scores=AbilityScores(
                strength=row.strength, dexterity=row.dexterity, constitution=row.constitution,
                intelligence=row.intelligence, wisdom=row.wisdom, charisma=row.charisma,
            ),
            class_equipment_option="package",
            class_equipment=[
                "Chain Mail", "Greatsword", "Longsword", "Light Crossbow", "20 Bolts", "Dungeoneer's Pack",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Insignia of Rank", "War Trophy", "Bone Dice", "Common Clothes", "10 GP",
            ],
            skill_proficiencies=["Athletics", "Intimidation", "Perception", "Survival"],
            fighting_style=row.fighting_styles[0],
            fighting_styles=list(row.fighting_styles),
            combat_loadout_kind="two-handed",
            feature_audits=_features(level),
            source_references=[
                "Basic Rules 2014: Human — Ability Score Increase",
                "Basic Rules 2014: Fighter — levels 1-10 and Champion",
                "Basic Rules 2014: Soldier background",
                "Basic Rules 2014: Equipment — Chain Mail, Greatsword, Light Crossbow",
            ],
        )
    except Exception:
        logger.exception("Failed to build 2014 Karnok profile level %s.", level)
        raise
