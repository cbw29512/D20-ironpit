from __future__ import annotations

from app.content.canonical_combat_build_policy import canonical_background_increases, canonical_base_ability_scores
from app.content.canonical_hero_policy import canonical_template_id
from app.content.canonical_progression import advance_profile_data
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
        combat_loadout_kind="dual-wield",
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



def build_mara_quickstep_level2_profile() -> CharacterBuildProfile:
    """Level 2 preserves Mara's build and adds the combat-relevant Cunning Action feature."""
    try:
        base = build_mara_quickstep_profile()
        return base.model_copy(update={
            "id": "build-mara-quickstep-l2",
            "template_id": canonical_template_id("rogue", 2),
            "level": 2,
            "feature_audits": [
                *base.feature_audits,
                _feature(
                    "cunning-action", "Cunning Action", "class",
                    combat_relevant=True, automated=True,
                    notes="Uses the shared bonus-action Dash/Disengage/Hide engine.",
                ),
            ],
            "source_references": [
                *base.source_references,
                "Basic Rules 2024: Rogue 2 — Cunning Action",
            ],
        })
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 2 profile could not be created.") from exc



def build_mara_quickstep_level3_profile() -> CharacterBuildProfile:
    """Level 3 adds Steady Aim and the Thief subclass without inventing utility-item combat."""
    try:
        base = build_mara_quickstep_level2_profile()
        return base.model_copy(update={
            "id": "build-mara-quickstep-l3",
            "template_id": canonical_template_id("rogue", 3),
            "level": 3,
            "subclass_id": "thief",
            "subclass_name": "Thief",
            "feature_audits": [
                *base.feature_audits,
                _feature(
                    "steady-aim", "Steady Aim", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Uses the shared stationary Bonus Action to grant Advantage "
                        "on the next legal attack this turn."
                    ),
                ),
                _feature(
                    "thief-fast-hands", "Fast Hands", "subclass",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Arena-inert for the current certified loadout: Mara has no "
                        "qualifying combat item whose Utilize or Magic action is modeled."
                    ),
                ),
                _feature(
                    "thief-second-story-work", "Second-Story Work", "subclass",
                    combat_relevant=False, automated=False,
                    notes="Arena-inert in the standard Iron Pit battlefield.",
                ),
            ],
            "source_references": [
                *base.source_references,
                "Basic Rules 2024: Rogue 3 — Steady Aim; Thief — Fast Hands and Second-Story Work",
            ],
        })
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 3 profile could not be created.") from exc



def build_mara_quickstep_level4_profile() -> CharacterBuildProfile:
    """Level 4 takes the canonical ASI as +1 Dexterity / +1 Constitution."""
    try:
        previous = build_mara_quickstep_level3_profile()
        data = advance_profile_data(previous, 4)
        data.update(
            advancement_increases=[
                AbilityIncrease(ability="dexterity", amount=1).model_dump(),
                AbilityIncrease(ability="constitution", amount=1).model_dump(),
            ],
            final_ability_scores=AbilityScores(
                strength=13, dexterity=18, constitution=16,
                intelligence=10, wisdom=10, charisma=10,
            ).model_dump(),
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "ability-score-improvement-l4",
                    "Ability Score Improvement",
                    "feat",
                    combat_relevant=True,
                    automated=True,
                    notes=(
                        "Canonical combat choice splits +1 Dexterity / +1 Constitution: "
                        "DEX 17→18 and CON 15→16."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 4 — Ability Score Improvement",
                "Basic Rules 2024: Feats — Ability Score Improvement (+1 Dexterity, +1 Constitution)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 4 profile could not be created.") from exc
