from __future__ import annotations

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def build_varek_ashenmark_2014_profile(level: int) -> CharacterBuildProfile:
    if level not in range(1, 5):
        raise ValueError("2014 Varek profile currently certifies levels 1 through 4.")
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
    advancement = [AbilityIncrease(ability="charisma", amount=2)] if level >= 4 else []
    final = AbilityScores(
        strength=9, dexterity=15, constitution=14,
        intelligence=11, wisdom=13, charisma=18 if level >= 4 else 16,
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
    if level >= 2:
        audits.extend([
            FeatureAudit(
                feature_id="agonizing-blast", feature_name="Agonizing Blast",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=True, automated=True,
                notes="Adds Charisma modifier to each certified Eldritch Blast beam through the spell-attack damage bonus field.",
            ),
            FeatureAudit(
                feature_id="eldritch-spear", feature_name="Eldritch Spear",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=True, automated=True,
                notes="Extends Eldritch Blast range to 300 feet without a new resolver.",
            ),
        ])
    if level >= 3:
        audits.append(
            FeatureAudit(
                feature_id="pact-of-the-tome", feature_name="Pact of the Tome",
                source_reference="D&D Basic Rules 2014: Pact Boon — Pact of the Tome",
                category="class", combat_relevant=False, automated=True,
                notes=(
                    "Canonical blaster boon. Its three bonus cantrips are retained as progression metadata; "
                    "Eldritch Blast remains the stronger certified arena attack, so Tome does not require a new resolver."
                ),
            )
        )
    if level >= 4:
        audits.append(
            FeatureAudit(
                feature_id="ability-score-improvement-l4", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 4",
                category="class", combat_relevant=True, automated=True,
                notes="Damage-first progression raises Charisma 16→18, improving spell attacks, save DC, and Agonizing Blast damage.",
            )
        )
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
