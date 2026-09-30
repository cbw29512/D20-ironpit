from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.druid_2024_profile_features import build_druid_2024_feature_audits
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_thalen_greenbough_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile Thalen's 2024 Druid foundation without early subclass leakage."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            raise ValueError("2024 Thalen profile currently supports Druid levels 1 through 9.")
        hero = HERO_BY_CLASS["druid"]
        base = canonical_base_ability_scores("druid")
        background_allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("druid", background_allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="wisdom", amount=1),
                AbilityIncrease(ability="charisma", amount=1),
            ])
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id=f"build-thalen-greenbough-l{level}",
            template_id=canonical_template_id("druid", level),
            character_name=hero.hero_name,
            class_id="druid",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            subclass_id="circle-land" if level >= 3 else None,
            subclass_name="Circle of the Land" if level >= 3 else None,
            build_id="land-damage",
            species_id="wood-elf",
            species_name="Wood Elf",
            background_id="acolyte",
            background_name="Acolyte",
            origin_feat_id="magic-initiate-cleric",
            origin_feat_name="Magic Initiate (Cleric)",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            advancement_increases=advancement,
            final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=[
                "Leather Armor", "Shield", "Sickle", "Druidic Focus (Quarterstaff)",
                "Explorer's Pack", "Herbalism Kit", "9 GP",
            ],
            background_equipment_option="package",
            background_equipment=[
                "Calligrapher's Supplies", "Book (prayers)", "Holy Symbol",
                "Parchment (10 sheets)", "Robe", "8 GP",
            ],
            skill_proficiencies=["Nature", "Survival", "Insight", "Religion", "Perception"],
            weapon_masteries=[],
            combat_loadout_kind=None,
            feature_audits=build_druid_2024_feature_audits(level),
            source_references=[
                "D&D Beyond Basic Rules 2024: Druid — Core Traits, Spellcasting, Druidic, Primal Order",
                "D&D Beyond Basic Rules 2024: Character Origins — Elf (Wood Elf), Acolyte",
                "D&D Beyond Basic Rules 2024: Feats — Magic Initiate",
                "D&D Beyond Basic Rules 2024: Equipment — Leather Armor, Shield, Sickle",
                "D&D Beyond Basic Rules 2024: Spells — Poison Spray, Healing Word, Cure Wounds, Longstrider, Faerie Fire",
                "D&D Beyond Basic Rules 2024: Druid 2 — Wild Shape, Wild Companion",
                *(
                    ["D&D Beyond Basic Rules 2024: Druid 4 — Ability Score Improvement; Starry Wisp"]
                    if level >= 4 else []
                ),
                *(
                    ["D&D Beyond Basic Rules 2024: Druid 5 — Wild Resurgence; level 3 spell slots"]
                    if level >= 5 else []
                ),
                *(
                    [
                        "D&D Beyond Basic Rules 2024: Circle of the Land 6 — Natural Recovery",
                        "D&D Beyond Basic Rules 2024: Spells — Aid",
                    ]
                    if level >= 6 else []
                ),
                *(
                    [
                        "D&D Beyond Basic Rules 2024: Druid 7 — Elemental Fury: Potent Spellcasting",
                        "D&D Beyond Basic Rules 2024: Circle of the Land 7 — Arid Circle Spell: Blight",
                        "D&D Beyond Basic Rules 2024: Spells — Divination",
                    ]
                    if level >= 7 else []
                ),
                *(
                    [
                        "D&D Beyond Basic Rules 2024: Druid 8 — Ability Score Improvement; Wild Shape improvement",
                        "D&D Beyond Basic Rules 2024: Spells — Freedom of Movement",
                    ]
                    if level >= 8 else []
                ),
                *(
                    [
                        "D&D Beyond Basic Rules 2024: Druid 9 — level 5 spell slots",
                        "D&D Beyond Basic Rules 2024: Spells — Cone of Cold, Mass Cure Wounds",
                        "D&D Beyond Basic Rules 2024: Circle of the Land 9 — Arid Circle Spell: Wall of Stone",
                    ]
                    if level >= 9 else []
                ),
                *(
                    ["D&D Beyond Basic Rules 2024: Circle of the Land 3 — Land's Aid, Circle Spells (Arid)"]
                    if level >= 3 else []
                ),
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Thalen Greenbough profile at level %s.", level)
        raise
