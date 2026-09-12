from __future__ import annotations

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


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
        source_reference="D&D Beyond Basic Rules 2024 / SRD 5.2.1",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
        notes=notes,
    )


def build_varek_ashenmark_profile() -> CharacterBuildProfile:
    hero = HERO_BY_CLASS["warlock"]
    base_scores = canonical_base_ability_scores("warlock")
    background_allowed = ["intelligence", "wisdom", "charisma"]
    return CharacterBuildProfile(
        id="build-varek-ashenmark-l1",
        template_id=canonical_template_id("warlock", 1),
        character_name=hero.hero_name,
        class_id="warlock",
        class_name=hero.class_name,
        level=1,
        species_id="orc",
        species_name="Orc",
        background_id="acolyte",
        background_name="Acolyte",
        origin_feat_id="magic-initiate-cleric",
        origin_feat_name="Magic Initiate (Cleric)",
        base_ability_scores=base_scores,
        background_allowed_abilities=background_allowed,
        background_increases=canonical_background_increases("warlock", background_allowed),
        final_ability_scores=base_scores.model_copy(update={"wisdom": 15, "charisma": 17}),
        class_equipment_option="package",
        class_equipment=[
            "Leather Armor", "Sickle", "2 Daggers", "Arcane Focus (orb)",
            "Book (occult lore)", "Scholar's Pack", "15 GP",
        ],
        background_equipment_option="package",
        background_equipment=[
            "Calligrapher's Supplies", "Book (prayers)", "Holy Symbol",
            "Parchment (10 sheets)", "Robe", "8 GP",
        ],
        skill_proficiencies=["Arcana", "Intimidation", "Insight", "Religion"],
        weapon_masteries=[],
        combat_loadout_kind=None,
        feature_audits=[
            _feature(
                "eldritch-invocations", "Eldritch Invocations", "class",
                combat_relevant=True, automated=False,
                notes="Pact of the Blade is fully represented by immutable weapon data, but the strict hero registry has not yet certified invocation data features.",
            ),
            _feature(
                "pact-of-the-blade", "Pact of the Blade", "class",
                combat_relevant=True, automated=True, runtime_attack_weapon_id="longsword",
                notes="Prepared runtime data uses a conjured Longsword with Charisma for attack and damage.",
            ),
            _feature(
                "pact-magic", "Pact Magic", "class",
                combat_relevant=True, automated=False,
                notes="The Pact slot is modeled, but the current canonical level-1 package is Charm Person plus Hex and is not fully certified.",
            ),
            _feature(
                "charm-person", "Charm Person", "class", combat_relevant=True, automated=False,
                notes="Blocked on complete Charmed-condition semantics in the universal engine.",
            ),
            _feature(
                "hex", "Hex", "class", combat_relevant=True, automated=False,
                notes="Blocked until the canonical Hex concentration, target transfer, and bonus-damage lifecycle is permanently certified.",
            ),
            _feature("eldritch-blast", "Eldritch Blast", "class", combat_relevant=True, automated=True),
            _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            _feature(
                "darkvision", "Darkvision", "species",
                combat_relevant=False, automated=False, notes="Iron Pit assumes sufficient arena visibility.",
            ),
            _feature(
                "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
                combat_relevant=False, automated=False,
                notes="Origin-feat utility choices do not alter the certified arena loop.",
            ),
            _feature("leather-armor", "Leather Armor", "equipment", combat_relevant=True, automated=True),
        ],
        source_references=[
            "Basic Rules 2024: Creating a Character — Point Buy",
            "Basic Rules 2024: Warlock — Core Traits, Eldritch Invocations, Pact Magic",
            "Basic Rules 2024: Eldritch Invocation Options — Pact of the Blade",
            "Basic Rules 2024: Character Origins — Acolyte and Orc",
            "Basic Rules 2024: Feats — Magic Initiate",
            "Basic Rules 2024: Equipment — Leather Armor and Longsword",
            "SRD 5.2.1: Eldritch Blast, Charm Person, Hex",
        ],
    )
