from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


FIGHTER_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="fighter", subclass_id="champion", subclass_name="Champion",
        role="two-handed", ability_priority=("strength", "constitution", "dexterity"),
        armor="chain-mail", shield=False, primary_weapon="greatsword",
        secondary_weapons=("shortbow",), fighting_style_priority=("Great Weapon Fighting", "Defense"),
        mastery_priority=("greatsword", "shortbow", "longsword", "shortsword", "scimitar"),
        source_reference="Player's Handbook 2024: Fighter, Champion, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="battle-master", subclass_name="Battle Master",
        role="dual-wield", ability_priority=("dexterity", "constitution", "wisdom"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        secondary_weapons=("scimitar", "longbow"), fighting_style_priority=("Two-Weapon Fighting",),
        mastery_priority=("shortsword", "scimitar", "longbow", "longsword", "greatsword"),
        source_reference="Player's Handbook 2024: Fighter, Battle Master, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="eldritch-knight", subclass_name="Eldritch Knight",
        role="sword-shield", ability_priority=("strength", "intelligence", "constitution"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        secondary_weapons=("shortbow",), fighting_style_priority=("Defense",),
        mastery_priority=("longsword", "shortbow", "greatsword", "shortsword", "scimitar"),
        spell_package_id="eldritch-knight",
        source_reference="Player's Handbook 2024: Fighter, Eldritch Knight, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="psi-warrior", subclass_name="Psi Warrior",
        role="ranged", ability_priority=("dexterity", "intelligence", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="longbow",
        secondary_weapons=("shortsword", "scimitar"), fighting_style_priority=("Archery",),
        mastery_priority=("longbow", "shortsword", "scimitar", "longsword", "greatsword"),
        source_reference="Player's Handbook 2024: Fighter, Psi Warrior, and Equipment",
    ),
)
