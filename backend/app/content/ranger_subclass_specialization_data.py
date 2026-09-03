from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


RANGER_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="ranger", subclass_id="hunter", subclass_name="Hunter",
        role="durable-melee", ability_priority=("dexterity", "wisdom", "constitution"),
        armor="studded-leather", shield=True, primary_weapon="shortsword",
        secondary_weapons=("longbow",), fighting_style_priority=("Defense",),
        mastery_priority=("shortsword", "longbow"), spell_package_id="hunter",
        feature_choice_ids=("hunter-prey-colossus-slayer", "hunter-multiattack-defense"),
        source_reference="Player's Handbook 2024: Ranger, Hunter, Fighting Style, Mastery, and Equipment",
    ),
    SubclassSpecialization(
        class_id="ranger", subclass_id="gloom-stalker", subclass_name="Gloom Stalker",
        role="ranged", ability_priority=("dexterity", "wisdom", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="longbow",
        secondary_weapons=("shortsword",), fighting_style_priority=("Archery",),
        mastery_priority=("longbow", "shortsword"), spell_package_id="gloom-stalker",
        source_reference="Player's Handbook 2024: Ranger, Gloom Stalker, Spells, Mastery, and Equipment",
    ),
    SubclassSpecialization(
        class_id="ranger", subclass_id="beastmaster", subclass_name="Beast Master",
        role="dual-wield", ability_priority=("dexterity", "wisdom", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        secondary_weapons=("scimitar", "longbow"), fighting_style_priority=("Two-Weapon Fighting",),
        mastery_priority=("shortsword", "scimitar"), spell_package_id="beastmaster",
        feature_choice_ids=("beastmaster-beast-of-the-land",),
        source_reference="Player's Handbook 2024: Ranger, Beast Master, Fighting Style, Mastery, and Equipment",
    ),
)
