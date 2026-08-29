from __future__ import annotations

from app.domain.character_builds import (
    AbilityIncrease,
    AbilityScores,
    CharacterBuildProfile,
    FeatureAudit,
)


def _feature(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        notes=notes,
    )


def build_karnok_stoneward_profile() -> CharacterBuildProfile:
    return CharacterBuildProfile(
        id="build-karnok-stoneward-l1",
        template_id="karnok-stoneward-l1",
        character_name="Karnok Stoneward",
        class_id="fighter",
        class_name="Fighter",
        level=1,
        species_id="orc",
        species_name="Orc",
        background_id="soldier",
        background_name="Soldier",
        origin_feat_id="savage-attacker",
        origin_feat_name="Savage Attacker",
        base_ability_scores=AbilityScores(
            strength=15,
            dexterity=13,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_allowed_abilities=["strength", "dexterity", "constitution"],
        background_increases=[
            AbilityIncrease(ability="strength", amount=2),
            AbilityIncrease(ability="constitution", amount=1),
        ],
        final_ability_scores=AbilityScores(
            strength=17,
            dexterity=13,
            constitution=15,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        class_equipment_option="package",
        class_equipment=[
            "Chain Mail",
            "Greatsword",
            "Flail",
            "8 Javelins",
            "Dungeoneer's Pack",
            "4 GP",
        ],
        background_equipment_option="package",
        background_equipment=[
            "Spear",
            "Shortbow",
            "20 Arrows",
            "Gaming Set",
            "Healer's Kit",
            "Quiver",
            "Traveler's Clothes",
            "14 GP",
        ],
        skill_proficiencies=["Athletics", "Intimidation", "Perception", "Survival"],
        weapon_masteries=["flail", "javelin", "spear"],
        fighting_style="Defense",
        feature_audits=[
            _feature("fighting-style-defense", "Defense", "class", combat_relevant=True, automated=True),
            _feature("second-wind", "Second Wind", "class", combat_relevant=True, automated=True),
            _feature(
                "weapon-mastery",
                "Weapon Mastery",
                "class",
                combat_relevant=True,
                automated=True,
                notes="Masteries are Flail, Javelin, and Spear; the automated primary Greatsword has no active mastery.",
            ),
            _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            _feature(
                "darkvision",
                "Darkvision",
                "species",
                combat_relevant=False,
                automated=False,
                notes="Iron Pit's standard arena assumes sufficient visibility.",
            ),
            _feature("savage-attacker", "Savage Attacker", "feat", combat_relevant=True, automated=True),
            _feature("chain-mail", "Chain Mail", "equipment", combat_relevant=True, automated=True),
            _feature("greatsword", "Greatsword", "equipment", combat_relevant=True, automated=True),
        ],
        source_references=[
            "Basic Rules 2024: Creating a Character — Standard Array",
            "Basic Rules 2024: Fighter — Core Traits and Level 1 Features",
            "Basic Rules 2024: Character Origins — Soldier and Orc",
            "Basic Rules 2024: Feats — Savage Attacker and Defense",
            "Basic Rules 2024: Equipment — Chain Mail and Greatsword",
        ],
    )
