from __future__ import annotations

from app.content.canonical_combat_build_policy import canonical_background_increases, canonical_base_ability_scores
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


def build_mara_quickstep_profile() -> CharacterBuildProfile:
    hero = HERO_BY_CLASS["rogue"]
    base_scores = canonical_base_ability_scores("rogue")
    background_allowed = ["strength", "dexterity", "constitution"]
    background_increases = canonical_background_increases("rogue", background_allowed)
    final_scores = base_scores.model_copy(update={"dexterity": 17, "constitution": 15})
    return CharacterBuildProfile(
        id="build-mara-quickstep-l1",
        template_id=canonical_template_id("rogue", 1),
        character_name=hero.hero_name,
        class_id="rogue",
        class_name=hero.class_name,
        level=1,
        species_id="orc",
        species_name="Orc",
        background_id="soldier",
        background_name="Soldier",
        origin_feat_id="savage-attacker",
        origin_feat_name="Savage Attacker",
        base_ability_scores=base_scores,
        background_allowed_abilities=background_allowed,
        background_increases=background_increases,
        final_ability_scores=final_scores,
        class_equipment_option="package",
        class_equipment=[
            "Leather Armor", "2 Daggers", "Shortsword", "Shortbow", "20 Arrows",
            "Quiver", "Thieves' Tools", "Burglar's Pack", "8 GP",
        ],
        background_equipment_option="package",
        background_equipment=[
            "Spear", "Shortbow", "20 Arrows", "Gaming Set", "Healer's Kit",
            "Quiver", "Traveler's Clothes", "14 GP",
        ],
        skill_proficiencies=["Athletics", "Intimidation", "Acrobatics", "Perception", "Sleight of Hand", "Stealth"],
        weapon_masteries=["shortsword", "shortbow"],
        feature_audits=[
            _feature("sneak-attack", "Sneak Attack", "class", combat_relevant=True, automated=True),
            _feature(
                "weapon-mastery", "Weapon Mastery", "class", combat_relevant=True, automated=True,
                notes="Shortsword and Shortbow both use the shared Vex mastery engine.",
            ),
            _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            _feature("savage-attacker", "Savage Attacker", "feat", combat_relevant=True, automated=True),
            _feature("leather-armor", "Leather Armor", "equipment", combat_relevant=True, automated=True),
            _feature(
                "shortsword", "Shortsword", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="shortsword",
            ),
            _feature(
                "shortbow", "Shortbow", "equipment", combat_relevant=True, automated=True,
                runtime_attack_weapon_id="shortbow",
            ),
        ],
        source_references=[
            "Basic Rules 2024: Creating a Character — Point Buy",
            "Basic Rules 2024: Rogue — Core Traits, Sneak Attack, Weapon Mastery, Starting Equipment",
            "Basic Rules 2024: Character Origins — Soldier and Orc",
            "Basic Rules 2024: Feats — Savage Attacker",
            "Basic Rules 2024: Equipment — Leather Armor, Shortsword, Shortbow, Vex",
        ],
    )
