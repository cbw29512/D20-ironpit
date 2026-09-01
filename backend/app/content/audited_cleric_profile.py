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
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
        notes=notes,
    )


def build_seraphine_dawnshield_profile() -> CharacterBuildProfile:
    hero = HERO_BY_CLASS["cleric"]
    base_scores = canonical_base_ability_scores("cleric")
    background_allowed = ["constitution", "intelligence", "wisdom"]
    background_increases = canonical_background_increases("cleric", background_allowed)
    final_scores = base_scores.model_copy(update={"wisdom": 17, "intelligence": 14})
    return CharacterBuildProfile(
        id="build-seraphine-dawnshield-l1",
        template_id=canonical_template_id("cleric", 1),
        character_name=hero.hero_name,
        class_id="cleric",
        class_name=hero.class_name,
        level=1,
        species_id="orc",
        species_name="Orc",
        background_id="sage",
        background_name="Sage",
        origin_feat_id="magic-initiate-wizard",
        origin_feat_name="Magic Initiate (Wizard)",
        base_ability_scores=base_scores,
        background_allowed_abilities=background_allowed,
        background_increases=background_increases,
        final_ability_scores=final_scores,
        class_equipment_option="package",
        class_equipment=["Chain Shirt", "Shield", "Mace", "Holy Symbol", "Priest's Pack", "7 GP"],
        background_equipment_option="package",
        background_equipment=[
            "Quarterstaff", "Calligrapher's Supplies", "Book (history)",
            "Parchment (8 sheets)", "Robe", "8 GP",
        ],
        skill_proficiencies=["Arcana", "History", "Medicine", "Persuasion"],
        weapon_masteries=[],
        combat_loadout_kind=None,
        feature_audits=[
            _feature("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
            _feature(
                "divine-order-protector", "Divine Order: Protector", "class",
                combat_relevant=False, automated=False,
                notes="Martial-weapon and Heavy-armor training are legal but unused by the certified chain-shirt, shield, and mace loadout.",
            ),
            _feature("sacred-flame", "Sacred Flame", "class", combat_relevant=True, automated=True),
            _feature("bless", "Bless", "class", combat_relevant=True, automated=True),
            _feature("cure-wounds", "Cure Wounds", "class", combat_relevant=True, automated=True),
            _feature("guiding-bolt", "Guiding Bolt", "class", combat_relevant=True, automated=True),
            _feature("shield-of-faith", "Shield of Faith", "class", combat_relevant=True, automated=True),
            _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            _feature(
                "darkvision", "Darkvision", "species", combat_relevant=False, automated=False,
                notes="Iron Pit assumes sufficient arena visibility.",
            ),
            _feature(
                "magic-initiate-wizard", "Magic Initiate (Wizard)", "feat",
                combat_relevant=False, automated=False,
                notes="Canonical utility choices are Mage Hand, Prestidigitation, and Identify; none alter arena combat.",
            ),
            _feature(
                "mace", "Mace", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="mace",
            ),
            _feature("chain-shirt-shield", "Chain Shirt and Shield", "equipment", combat_relevant=True, automated=True),
        ],
        source_references=[
            "Basic Rules 2024: Creating a Character — Point Buy",
            "Basic Rules 2024: Cleric — Core Traits, Spellcasting, Divine Order",
            "Basic Rules 2024: Character Origins — Sage and Orc",
            "Basic Rules 2024: Feats — Magic Initiate",
            "Basic Rules 2024: Equipment — Chain Shirt, Shield, Mace",
            "Basic Rules 2024: Spells — Sacred Flame, Bless, Cure Wounds, Guiding Bolt, Shield of Faith",
        ],
    )


def build_seraphine_dawnshield_level2_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_profile()
    additions = [
        _feature("healing-word", "Healing Word", "class", combat_relevant=True, automated=True),
        _feature("channel-divinity", "Channel Divinity", "class", combat_relevant=True, automated=True),
        _feature("divine-spark", "Divine Spark", "class", combat_relevant=True, automated=True),
        _feature("turn-undead", "Turn Undead", "class", combat_relevant=True, automated=True),
    ]
    return base.model_copy(update={
        "id": "build-seraphine-dawnshield-l2",
        "template_id": canonical_template_id("cleric", 2),
        "level": 2,
        "feature_audits": [*base.feature_audits, *additions],
        "source_references": [
            *base.source_references,
            "Basic Rules 2024: Cleric level 2 — Channel Divinity, Divine Spark, Turn Undead",
            "Basic Rules 2024: Spells — Healing Word",
        ],
    })
