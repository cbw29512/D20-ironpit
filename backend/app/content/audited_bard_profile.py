from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


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
        source_reference="D&D Beyond Basic Rules 2024: Bard",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
        notes=notes,
    )


def _scores() -> tuple[AbilityScores, list, AbilityScores]:
    base = canonical_base_ability_scores("bard")
    allowed = ["intelligence", "wisdom", "charisma"]
    increases = canonical_background_increases("bard", allowed)
    values = base.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return base, increases, AbilityScores(**values)


def _audits(level: int) -> list[FeatureAudit]:
    audits = [
        _feature("bardic-inspiration", "Bardic Inspiration", "class", combat_relevant=True, automated=True),
        _feature("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
        _feature("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
        _feature("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
        _feature(
            "darkvision", "Darkvision", "species", combat_relevant=False, automated=False,
            notes="Iron Pit's standard arena assumes sufficient visibility.",
        ),
        _feature(
            "magic-initiate-cleric", "Magic Initiate (Cleric)", "feat",
            combat_relevant=False, automated=False,
            notes="Canonical feat choices are Light, Thaumaturgy, and Detect Magic; none alter arena combat.",
        ),
        _feature(
            "dagger", "Dagger", "equipment", combat_relevant=True, automated=True,
            runtime_attack_weapon_id="dagger",
        ),
        _feature(
            "studded-leather", "Studded Leather Armor", "equipment",
            combat_relevant=True, automated=True,
        ),
    ]
    if level >= 2:
        audits.extend([
            _feature(
                "expertise", "Expertise", "class", combat_relevant=True, automated=True,
                notes="Acrobatics and Performance are Lyra's two Expertise choices.",
            ),
            _feature(
                "jack-of-all-trades", "Jack of All Trades", "class",
                combat_relevant=True, automated=True,
                notes="Half proficiency applies to unproficient skill checks such as Athletics, but not Initiative.",
            ),
        ])
    if level >= 3:
        audits.extend([
            _feature(
                "lore-bonus-proficiencies", "Bonus Proficiencies", "subclass",
                combat_relevant=True, automated=True,
                notes="College of Lore choices are Athletics, Deception, and Investigation.",
            ),
            _feature(
                "cutting-words", "Cutting Words", "subclass",
                combat_relevant=True, automated=True,
            ),
        ])
    return audits


def build_lyra_silverstring_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Lyra's legal 2024 Lore Bard progression through level 3."""
    try:
        if level not in {1, 2, 3}:
            raise ValueError("2024 Lyra progression currently certifies Bard levels 1 through 3.")
        hero = HERO_BY_CLASS["bard"]
        base, background_increases, final = _scores()
        skills = ["Acrobatics", "Perception", "Performance", "Insight", "Religion"]
        if level >= 3:
            skills.extend(["Athletics", "Deception", "Investigation"])
        return CharacterBuildProfile(
            id=f"build-lyra-silverstring-l{level}",
            template_id=canonical_template_id("bard", level),
            character_name=hero.hero_name,
            class_id="bard",
            class_name=hero.class_name,
            level=level,
            subclass_id="college-lore" if level >= 3 else None,
            subclass_name="College of Lore" if level >= 3 else None,
            build_id="support-healer",
            species_id="orc",
            species_name="Orc",
            background_id="acolyte",
            background_name="Acolyte",
            origin_feat_id="magic-initiate-cleric",
            origin_feat_name="Magic Initiate (Cleric)",
            base_ability_scores=base,
            background_allowed_abilities=["intelligence", "wisdom", "charisma"],
            background_increases=background_increases,
            final_ability_scores=final,
            class_equipment_option="gold",
            class_equipment=["Studded Leather Armor", "Dagger", "Lute"],
            background_equipment_option="package",
            background_equipment=[
                "Calligrapher's Supplies", "Book (prayers)", "Holy Symbol",
                "Parchment (10 sheets)", "Robe", "8 GP",
            ],
            skill_proficiencies=skills,
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Bard — Core Traits, Bardic Inspiration, Spellcasting",
                "D&D Beyond Basic Rules 2024: Acolyte background",
                "D&D Beyond Basic Rules 2024: Orc species",
                "D&D Beyond Basic Rules 2024: Studded Leather Armor and Dagger",
                *(["D&D Beyond Basic Rules 2024: Bard 2 — Expertise, Jack of All Trades"] if level >= 2 else []),
                *(["D&D Beyond Basic Rules 2024: College of Lore 3 — Bonus Proficiencies, Cutting Words"] if level >= 3 else []),
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Lyra Silverstring profile at level %s.", level)
        raise


def build_lyra_silverstring_level1_profile() -> CharacterBuildProfile:
    return build_lyra_silverstring_profile(1)


def build_lyra_silverstring_level2_profile() -> CharacterBuildProfile:
    return build_lyra_silverstring_profile(2)


def build_lyra_silverstring_level3_profile() -> CharacterBuildProfile:
    return build_lyra_silverstring_profile(3)
