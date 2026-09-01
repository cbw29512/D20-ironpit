from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def _feature(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    runtime_attack_weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
        notes=notes,
    )


def build_rokhan_stonefury_profile() -> CharacterBuildProfile:
    hero = HERO_BY_CLASS["barbarian"]
    return CharacterBuildProfile(
        id="build-rokhan-stonefury-l1",
        template_id=canonical_template_id("barbarian", 1),
        character_name=hero.hero_name,
        class_id="barbarian",
        class_name=hero.class_name,
        level=1,
        species_id="orc",
        species_name="Orc",
        background_id="soldier",
        background_name="Soldier",
        origin_feat_id="savage-attacker",
        origin_feat_name="Savage Attacker",
        base_ability_scores=AbilityScores(
            strength=15, dexterity=13, constitution=14,
            intelligence=8, wisdom=12, charisma=10,
        ),
        background_allowed_abilities=["strength", "dexterity", "constitution"],
        background_increases=[
            AbilityIncrease(ability="strength", amount=2),
            AbilityIncrease(ability="constitution", amount=1),
        ],
        final_ability_scores=AbilityScores(
            strength=17, dexterity=13, constitution=15,
            intelligence=8, wisdom=12, charisma=10,
        ),
        class_equipment_option="package",
        class_equipment=["Greataxe", "4 Handaxes", "Explorer's Pack", "15 GP"],
        background_equipment_option="package",
        background_equipment=[
            "Spear", "Shortbow", "20 Arrows", "Gaming Set", "Healer's Kit",
            "Quiver", "Traveler's Clothes", "14 GP",
        ],
        skill_proficiencies=["Athletics", "Intimidation", "Perception", "Survival"],
        weapon_masteries=["flail", "pike"],
        combat_loadout_kind="two-handed",
        feature_audits=[
            _feature("rage", "Rage", "class", combat_relevant=True, automated=True),
            _feature("unarmored-defense", "Unarmored Defense", "class", combat_relevant=True, automated=True),
            _feature(
                "weapon-mastery", "Weapon Mastery", "class",
                combat_relevant=False, automated=False,
                notes="Legal masteries are Flail and Pike. Rokhan's arena loadout uses Greataxe and Handaxe, so neither selected mastery is invoked.",
            ),
            _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            _feature(
                "darkvision", "Darkvision", "species", combat_relevant=False, automated=False,
                notes="Iron Pit's standard arena assumes sufficient visibility.",
            ),
            _feature("savage-attacker", "Savage Attacker", "feat", combat_relevant=True, automated=True),
            _feature(
                "greataxe", "Greataxe", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="greataxe",
            ),
            _feature(
                "handaxe", "Handaxe", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="handaxe",
                notes="One Handaxe is used for the single opening ranged attack before closing to melee.",
            ),
        ],
        source_references=[
            "Basic Rules 2024: Creating a Character — Standard Array",
            "Basic Rules 2024: Barbarian — Core Traits and Level 1 Features",
            "Basic Rules 2024: Character Origins — Soldier and Orc",
            "Basic Rules 2024: Feats — Savage Attacker",
            "Basic Rules 2024: Equipment — Greataxe and Handaxe",
        ],
    )
