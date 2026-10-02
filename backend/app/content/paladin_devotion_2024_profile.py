from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import canonical_background_increases, canonical_base_ability_scores
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _feature(
    feature_id: str, name: str, category: str, *, combat: bool, automated: bool,
    weapon_id: str | None = None, notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id, feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024", category=category,
        combat_relevant=combat, automated=automated,
        runtime_attack_weapon_id=weapon_id, notes=notes,
    )


def build_aurelia_brightshield_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Aurelia's legal 2024 Devotion Paladin progression through level 2."""
    try:
        if level not in {1, 2}:
            raise ValueError("The current 2024 Paladin profile tranche supports levels 1-2 only.")
        hero = HERO_BY_CLASS["paladin"]
        base = canonical_base_ability_scores("paladin")
        allowed = ["strength", "dexterity", "constitution"]
        background = canonical_background_increases("paladin", allowed)
        values = base.model_dump()
        for increase in background:
            values[increase.ability] += increase.amount
        final = type(base)(**values)

        audits = [
            _feature("lay-on-hands", "Lay On Hands", "class", combat=True, automated=True),
            _feature(
                "spellcasting", "Spellcasting", "class", combat=True, automated=True,
                notes=(
                    "Damage/healing-first preparation uses Cure Wounds and Divine Favor; "
                    "level 2 adds certified Bless while Divine Smite is always prepared separately."
                ),
            ),
            _feature(
                "weapon-mastery", "Weapon Mastery", "class", combat=True, automated=True,
                notes="Longsword uses Sap; Javelin uses Slow.",
            ),
            _feature("resourceful", "Resourceful", "species", combat=True, automated=True),
            _feature("skillful", "Skillful", "species", combat=False, automated=False),
            _feature("versatile-skilled", "Versatile: Skilled", "species", combat=False, automated=False),
            _feature("savage-attacker", "Savage Attacker", "feat", combat=True, automated=True),
            _feature("chain-mail", "Chain Mail", "equipment", combat=True, automated=True),
            _feature("shield", "Shield", "equipment", combat=True, automated=True),
            _feature("longsword", "Longsword", "equipment", combat=True, automated=True, weapon_id="longsword"),
            _feature("javelin", "Javelin", "equipment", combat=True, automated=True, weapon_id="javelin"),
        ]
        if level >= 2:
            audits.extend([
                _feature(
                    "fighting-style-defense", "Defense", "class", combat=True, automated=True,
                    notes="Fighting Style feat grants +1 AC while Aurelia wears Chain Mail.",
                ),
                _feature(
                    "paladins-smite", "Paladin's Smite", "class", combat=True, automated=True,
                    notes=(
                        "Divine Smite is always prepared and has one Long-Rest free cast. "
                        "Its damage joins the triggering attack's damage roll."
                    ),
                ),
            ])

        return CharacterBuildProfile(
            id=f"build-aurelia-brightshield-2024-l{level}",
            template_id=canonical_template_id("paladin", level),
            character_name=hero.hero_name, class_id="paladin", class_name=hero.class_name,
            level=level, ruleset="2024", build_id="devotion-sword-shield",
            species_id="human", species_name="Human",
            background_id="soldier", background_name="Soldier",
            origin_feat_id="savage-attacker", origin_feat_name="Savage Attacker",
            base_ability_scores=base, background_allowed_abilities=allowed,
            background_increases=background, final_ability_scores=final,
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
            source_references=[
                "Basic Rules 2024: Paladin — Lay On Hands, Spellcasting, Weapon Mastery",
                *(["Basic Rules 2024: Paladin level 2 — Fighting Style and Paladin's Smite"] if level >= 2 else []),
                "Basic Rules 2024: Character Origins — Human and Soldier",
                "Basic Rules 2024: Spells — Cure Wounds, Divine Favor, Bless, Divine Smite",
                "Basic Rules 2024: Equipment — Chain Mail, Shield, Longsword, Javelin, Sap, Slow",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Aurelia Brightshield profile at level %s.", level)
        raise
