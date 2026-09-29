from __future__ import annotations

import logging

from app.content.bard_2024_high_profile_support import (
    bard_level13_spells_audit,
    bard_level14_peerless_skill_audit,
    bard_level15_spells_audit,
    bard_level16_asi_audit,
    bard_level17_spells_audit,
    bard_level18_superior_inspiration_audit,
)
from app.content.bard_2024_lore_profile_support import (
    bard_level4_asi_audit,
    bard_level5_font_audit,
    bard_level6_magical_discoveries_audit,
    bard_level7_countercharm_audit,
    bard_level8_asi_audit,
    bard_level9_audits,
    bard_level10_magical_secrets_audit,
    bard_level12_asi_audit,
    lore_bard_level3_audits,
)
from app.content.bard_2024_profile_core import (
    bard_ability_scores,
    bard_feature_audit,
    bard_source_references,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)

def build_lyra_silverstring_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Lyra's legal 2024 Lore Bard progression through level 18."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}:
            raise ValueError("2024 Lyra profile currently certifies Bard levels 1 through 18.")
        hero = HERO_BY_CLASS["bard"]
        base, background_increases, advancement_increases, final = bard_ability_scores(level)
        audits = [
            bard_feature_audit("bardic-inspiration", "Bardic Inspiration", "class", combat_relevant=True, automated=True),
            bard_feature_audit("spellcasting", "Spellcasting", "class", combat_relevant=True, automated=True),
            bard_feature_audit("adrenaline-rush", "Adrenaline Rush", "species", combat_relevant=True, automated=True),
            bard_feature_audit("relentless-endurance", "Relentless Endurance", "species", combat_relevant=True, automated=True),
            bard_feature_audit(
                "darkvision",
                "Darkvision",
                "species",
                combat_relevant=False,
                automated=False,
                notes="Iron Pit's standard arena assumes sufficient visibility.",
            ),
            bard_feature_audit(
                "magic-initiate-cleric",
                "Magic Initiate (Cleric)",
                "feat",
                combat_relevant=False,
                automated=False,
                notes="Canonical feat choices are Light, Thaumaturgy, and Detect Magic; none alter arena combat.",
            ),
            bard_feature_audit(
                "dagger",
                "Dagger",
                "equipment",
                combat_relevant=True,
                automated=True,
                runtime_attack_weapon_id="dagger",
            ),
            bard_feature_audit(
                "studded-leather",
                "Studded Leather Armor",
                "equipment",
                combat_relevant=True,
                automated=True,
            ),
        ]
        if level >= 2:
            audits.extend([
                bard_feature_audit(
                    "expertise",
                    "Expertise",
                    "class",
                    combat_relevant=True,
                    automated=True,
                    notes="Acrobatics is the combat-relevant Expertise choice for grapple escape checks.",
                ),
                bard_feature_audit(
                    "jack-of-all-trades",
                    "Jack of All Trades",
                    "class",
                    combat_relevant=False,
                    automated=True,
                    notes="The automated arena uses Lyra's proficient Acrobatics for grapple escape; initiative is not a skill check.",
                ),
            ])
        if level >= 3:
            audits.extend(lore_bard_level3_audits())
        if level >= 4:
            audits.append(bard_level4_asi_audit())
        if level >= 5:
            audits.append(bard_level5_font_audit())
        if level >= 6:
            audits.append(bard_level6_magical_discoveries_audit())
        if level >= 7:
            audits.append(bard_level7_countercharm_audit())
        if level >= 8:
            audits.append(bard_level8_asi_audit())
        if level >= 9:
            audits.extend(bard_level9_audits())
        if level >= 10:
            audits.append(bard_level10_magical_secrets_audit())
        if level >= 12:
            audits.append(bard_level12_asi_audit())
        if level >= 13:
            audits.append(bard_level13_spells_audit())
        if level >= 14:
            audits.append(bard_level14_peerless_skill_audit())
        if level >= 15:
            audits.append(bard_level15_spells_audit())
        if level >= 16:
            audits.append(bard_level16_asi_audit())
        if level >= 17:
            audits.append(bard_level17_spells_audit())
        if level >= 18:
            audits.append(bard_level18_superior_inspiration_audit())
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
            advancement_increases=advancement_increases,
            final_ability_scores=final,
            class_equipment_option="gold",
            class_equipment=["Studded Leather Armor", "Dagger", "Lute"],
            background_equipment_option="package",
            background_equipment=[
                "Calligrapher's Supplies", "Book (prayers)", "Holy Symbol",
                "Parchment (10 sheets)", "Robe", "8 GP",
            ],
            skill_proficiencies=[
                "Acrobatics", "Perception", "Performance", "Insight", "Religion",
                *(["Arcana", "Deception", "Sleight of Hand"] if level >= 3 else []),
            ],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=audits,
            source_references=bard_source_references(level),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Lyra Silverstring profile at level %s.", level)
        raise
