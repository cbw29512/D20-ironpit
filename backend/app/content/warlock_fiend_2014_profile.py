from __future__ import annotations

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def build_varek_ashenmark_2014_profile(level: int) -> CharacterBuildProfile:
    if level != 1:
        raise ValueError("2014 Varek profile currently certifies level 1 only.")
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
    final = AbilityScores(
        strength=9, dexterity=15, constitution=14,
        intelligence=11, wisdom=13, charisma=16,
    )
    audits = [
        FeatureAudit(
            feature_id="pact-magic", feature_name="Pact Magic",
            source_reference="D&D Basic Rules 2014: Warlock 1",
            category="class", combat_relevant=True, automated=True,
            notes="One 1st-level Pact Magic slot is represented by the shared spell-slot resource model.",
        ),
        FeatureAudit(
            feature_id="fiend-patron", feature_name="The Fiend",
            source_reference="D&D Basic Rules 2014: Otherworldly Patron — The Fiend",
            category="subclass", combat_relevant=True, automated=True,
            notes="2014 patron begins at level 1; Expanded Spell List adds choices rather than automatic known spells.",
        ),
        FeatureAudit(
            feature_id="dark-ones-blessing", feature_name="Dark One's Blessing",
            source_reference="D&D Basic Rules 2014: The Fiend 1",
            category="subclass", combat_relevant=True, automated=True,
            notes="Uses the universal hostile-zeroing trigger and Temporary HP primitive.",
        ),
        FeatureAudit(
            feature_id="eldritch-blast", feature_name="Eldritch Blast",
            source_reference="D&D Basic Rules 2014: Eldritch Blast",
            category="class", combat_relevant=True, automated=True,
            notes="Uses the universal ranged spell-attack and force-damage primitives.",
        ),
        FeatureAudit(
            feature_id="hex", feature_name="Hex",
            source_reference="D&D Basic Rules 2014: Hex",
            category="class", combat_relevant=True, automated=True,
            notes="Selected for the damage-first canonical build. Uses the reusable targeted concentration bonus-damage primitive shared with Hunter's Mark.",
        ),
    ]
    return CharacterBuildProfile(
        id="build-varek-ashenmark-2014-l1",
        template_id="varek-ashenmark-2014-l1",
        character_name="Varek Ashenmark",
        class_id="warlock", class_name="Warlock", level=1, ruleset="2014",
        subclass_id="fiend-patron", subclass_name="Fiend Patron", build_id="eldritch-blaster",
        species_id="human", species_name="Human",
        background_id="sage", background_name="Sage",
        base_ability_scores=base, species_increases=increases,
        advancement_increases=[], final_ability_scores=final,
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
