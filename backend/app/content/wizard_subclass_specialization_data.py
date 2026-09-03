from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


WIZARD_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="wizard", subclass_id="evoker", subclass_name="Evoker",
        role="fire-blaster", ability_priority=("intelligence", "wisdom", "charisma"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="evoker", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Wizard, Evoker, and Wizard Spells",
    ),
    SubclassSpecialization(
        class_id="wizard", subclass_id="illusionist", subclass_name="Illusionist",
        role="control", ability_priority=("intelligence", "wisdom", "charisma"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="illusionist", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Wizard, Illusionist, and Wizard Spells",
    ),
    SubclassSpecialization(
        class_id="wizard", subclass_id="abjurer", subclass_name="Abjurer",
        role="balanced-arcane", ability_priority=("intelligence", "wisdom", "charisma"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="abjurer", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Wizard, Abjurer, and Wizard Spells",
    ),
)
