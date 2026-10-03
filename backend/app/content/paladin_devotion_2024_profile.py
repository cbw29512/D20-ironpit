from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.paladin_devotion_2024_build_support import build_paladin_2024_ability_progression
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.paladin_devotion_2024_profile_support import (
    paladin_2024_feature,
    paladin_2024_level5_audits,
    paladin_2024_level6_audits,
    paladin_2024_level7_audits,
    paladin_2024_source_references,
)
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_aurelia_brightshield_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Aurelia's legal 2024 Devotion Paladin progression through level 7."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7}:
            raise ValueError("The current 2024 Paladin profile tranche supports levels 1-7 only.")
        hero = HERO_BY_CLASS["paladin"]
        base, allowed, background, advancement, final = (
            build_paladin_2024_ability_progression(level)
        )

        audits = [
            paladin_2024_feature("lay-on-hands", "Lay On Hands", "class", combat=True, automated=True),
            paladin_2024_feature(
                "spellcasting", "Spellcasting", "class", combat=True, automated=True,
                notes=(
                    "Damage/healing-first preparation uses Cure Wounds and Divine Favor; "
                    "level 2 adds certified Bless while Divine Smite is always prepared separately."
                ),
            ),
            paladin_2024_feature(
                "weapon-mastery", "Weapon Mastery", "class", combat=True, automated=True,
                notes="Longsword uses Sap; Javelin uses Slow.",
            ),
            paladin_2024_feature("resourceful", "Resourceful", "species", combat=True, automated=True),
            paladin_2024_feature("skillful", "Skillful", "species", combat=False, automated=False),
            paladin_2024_feature("versatile-skilled", "Versatile: Skilled", "species", combat=False, automated=False),
            paladin_2024_feature("savage-attacker", "Savage Attacker", "feat", combat=True, automated=True),
            paladin_2024_feature("chain-mail", "Chain Mail", "equipment", combat=True, automated=True),
            paladin_2024_feature("shield", "Shield", "equipment", combat=True, automated=True),
            paladin_2024_feature("longsword", "Longsword", "equipment", combat=True, automated=True, weapon_id="longsword"),
            paladin_2024_feature("javelin", "Javelin", "equipment", combat=True, automated=True, weapon_id="javelin"),
        ]
        if level >= 2:
            audits.extend([
                paladin_2024_feature(
                    "fighting-style-defense", "Defense", "class", combat=True, automated=True,
                    notes="Fighting Style feat grants +1 AC while Aurelia wears Chain Mail.",
                ),
                paladin_2024_feature(
                    "paladins-smite", "Paladin's Smite", "class", combat=True, automated=True,
                    notes=(
                        "Divine Smite is always prepared and has one Long-Rest free cast. "
                        "Its damage joins the triggering attack's damage roll."
                    ),
                ),
            ])
        if level >= 3:
            audits.extend([
                paladin_2024_feature(
                    "channel-divinity", "Channel Divinity", "class", combat=True, automated=True,
                    notes="Two source-owned uses feed universal Channel Divinity consumers.",
                ),
                paladin_2024_feature(
                    "divine-sense", "Divine Sense", "class", combat=False, automated=False,
                    notes=(
                        "Arena state already exposes combatant creature type and position; "
                        "the detection feature does not change a current Iron Pit combat outcome."
                    ),
                ),
                paladin_2024_feature(
                    "sacred-weapon", "Sacred Weapon", "subclass", combat=True, automated=True,
                    notes=(
                        "Taking the Attack action spends one Channel Divinity to bind a 10-minute "
                        "weapon-scoped Charisma attack bonus and Radiant damage-type choice through "
                        "the universal Attack-action weapon-buff primitive."
                    ),
                ),
                paladin_2024_feature(
                    "oath-spells-level3", "Oath of Devotion Spells", "subclass",
                    combat=True, automated=True,
                    notes=(
                        "Protection from Evil and Good and Shield of Faith are always prepared with "
                        "explicit 2024 modifier fingerprints."
                    ),
                ),
            ])
        if level >= 4:
            audits.append(
                paladin_2024_feature(
                    "ability-score-improvement-l4",
                    "Ability Score Improvement (+2 Strength)",
                    "feat",
                    combat=True,
                    automated=True,
                    notes=(
                        "Canonical sword-and-shield progression raises Strength 17 to 19; "
                        "shared derived-stat logic updates weapon attack/damage and Athletics."
                    ),
                )
            )
        if level >= 5:
            audits.extend(paladin_2024_level5_audits())
        if level >= 6:
            audits.extend(paladin_2024_level6_audits())
        if level >= 7:
            audits.extend(paladin_2024_level7_audits())

        return CharacterBuildProfile(
            id=f"build-aurelia-brightshield-2024-l{level}",
            template_id=canonical_template_id("paladin", level),
            character_name=hero.hero_name, class_id="paladin", class_name=hero.class_name,
            level=level, ruleset="2024", build_id="devotion-sword-shield",
            subclass_id="oath-devotion" if level >= 3 else None,
            subclass_name="Oath of Devotion" if level >= 3 else None,
            species_id="human", species_name="Human",
            background_id="soldier", background_name="Soldier",
            origin_feat_id="savage-attacker", origin_feat_name="Savage Attacker",
            base_ability_scores=base, background_allowed_abilities=allowed,
            background_increases=background, advancement_increases=advancement,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Chain Mail", "Shield", "Longsword", "6 Javelins",
                "Holy Symbol", "Priest's Pack", "9 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Spear", "Shortbow", "20 Arrows", "Gaming Set", "Healer's Kit",
                "Quiver", "Traveler's Clothes", "14 GP",
            ],
            skill_proficiencies=[
                "Athletics", "Intimidation", "Insight", "Persuasion",
                "Perception", "Acrobatics", "Medicine", "Religion",
            ],
            weapon_masteries=["longsword", "javelin"],
            fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [],
            combat_loadout_kind="one-hander-shield",
            feature_audits=audits,
            source_references=paladin_2024_source_references(level),
        )
    except Exception:
        logger.exception("Failed to compile 2024 Aurelia Brightshield profile at level %s.", level)
        raise
