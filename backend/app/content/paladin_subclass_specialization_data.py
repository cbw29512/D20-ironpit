from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


PALADIN_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="paladin", subclass_id="oath-devotion", subclass_name="Oath of Devotion",
        role="sword-shield", ability_priority=("strength", "charisma", "constitution"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        secondary_weapons=("battleaxe",), fighting_style_priority=("Defense",),
        mastery_priority=("longsword", "battleaxe"), spell_package_id="oath-devotion",
        source_reference="Player's Handbook 2024: Paladin, Oath of Devotion, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="paladin", subclass_id="oath-vengeance", subclass_name="Oath of Vengeance",
        role="two-handed", ability_priority=("strength", "charisma", "constitution"),
        armor="chain-mail", shield=False, primary_weapon="greatsword",
        secondary_weapons=("longsword",), fighting_style_priority=("Great Weapon Fighting",),
        mastery_priority=("greatsword", "longsword"), spell_package_id="oath-vengeance",
        source_reference="Player's Handbook 2024: Paladin, Oath of Vengeance, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="paladin", subclass_id="oath-ancients", subclass_name="Oath of the Ancients",
        role="support-healing", ability_priority=("strength", "charisma", "constitution"),
        armor="chain-mail", shield=True, primary_weapon="battleaxe",
        secondary_weapons=("longsword",), fighting_style_priority=("Defense",),
        mastery_priority=("battleaxe", "longsword"), spell_package_id="oath-ancients",
        source_reference="Player's Handbook 2024: Paladin, Oath of the Ancients, Spells, and Equipment",
    ),
)
