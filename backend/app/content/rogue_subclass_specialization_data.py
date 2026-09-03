from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


ROGUE_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="rogue", subclass_id="thief", subclass_name="Thief",
        role="dual-wield", ability_priority=("dexterity", "constitution", "wisdom"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        secondary_weapons=("scimitar", "shortbow"), mastery_priority=("shortsword", "scimitar"),
        source_reference="Player's Handbook 2024: Rogue, Thief, Weapon Mastery, and Equipment",
    ),
    SubclassSpecialization(
        class_id="rogue", subclass_id="assassin", subclass_name="Assassin",
        role="ranged", ability_priority=("dexterity", "constitution", "wisdom"),
        armor="studded-leather", shield=False, primary_weapon="shortbow",
        secondary_weapons=("shortsword",), mastery_priority=("shortbow", "shortsword"),
        source_reference="Player's Handbook 2024: Rogue, Assassin, Weapon Mastery, and Equipment",
    ),
    SubclassSpecialization(
        class_id="rogue", subclass_id="arcane-trickster", subclass_name="Arcane Trickster",
        role="finesse-duelist", ability_priority=("dexterity", "intelligence", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="rapier",
        secondary_weapons=("shortbow",), mastery_priority=("rapier", "shortbow"),
        spell_package_id="arcane-trickster", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Rogue, Arcane Trickster, Spellcasting, Mastery, and Equipment",
    ),
)
