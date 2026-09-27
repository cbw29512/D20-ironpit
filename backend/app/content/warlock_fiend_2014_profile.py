from __future__ import annotations

from app.content.warlock_fiend_2014_audits import build_varek_fiend_2014_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def build_varek_ashenmark_2014_profile(level: int) -> CharacterBuildProfile:
    if level not in range(1, 16):
        raise ValueError("2014 Varek profile currently certifies levels 1 through 15.")
    base = AbilityScores(
        strength=8, dexterity=14, constitution=13,
        intelligence=10, wisdom=12, charisma=15,
    )
    increases = [
        AbilityIncrease(ability="strength", amount=1),
        AbilityIncrease(ability="dexterity", amount=1),
        AbilityIncrease(ability="constitution", amount=1),
        AbilityIncrease(ability="intelligence", amount=1),
        AbilityIncrease(ability="wisdom", amount=1),
        AbilityIncrease(ability="charisma", amount=1),
    ]
    advancement = (
        ([AbilityIncrease(ability="charisma", amount=2)] if level >= 4 else [])
        + ([AbilityIncrease(ability="charisma", amount=2)] if level >= 8 else [])
        + ([AbilityIncrease(ability="constitution", amount=2)] if level >= 12 else [])
    )
    final = AbilityScores(
        strength=9, dexterity=15, constitution=16 if level >= 12 else 14,
        intelligence=11, wisdom=13, charisma=20 if level >= 8 else 18 if level >= 4 else 16,
    )
    audits = build_varek_fiend_2014_audits(level)
    return CharacterBuildProfile(
        id=f"build-varek-ashenmark-2014-l{level}",
        template_id=f"varek-ashenmark-2014-l{level}",
        character_name="Varek Ashenmark",
        class_id="warlock", class_name="Warlock", level=level, ruleset="2014",
        subclass_id="fiend-patron", subclass_name="Fiend Patron", build_id="eldritch-blaster",
        species_id="human", species_name="Human",
        background_id="sage", background_name="Sage",
        base_ability_scores=base, species_increases=increases,
        advancement_increases=advancement, final_ability_scores=final,
        class_equipment_option="package",
        class_equipment=[
            "Leather Armor", "Light Crossbow", "20 Bolts", "Component Pouch",
            "Dungeoneer's Pack", "Quarterstaff", "Dagger", "Dagger",
        ],
        background_equipment_option="package",
        background_equipment=["Bottle of Black Ink", "Quill", "Small Knife", "Letter", "Common Clothes", "10 gp"],
        skill_proficiencies=["Arcana", "History"],
        weapon_masteries=[], combat_loadout_kind=None,
        feature_audits=audits,
        source_references=[
            "D&D Basic Rules 2014: Human",
            "D&D Basic Rules 2014: Sage",
            "D&D Basic Rules 2014: Warlock",
            "D&D Basic Rules 2014: The Fiend",
            "D&D Basic Rules 2014: Equipment",
        ],
    )
