from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


BARD_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="bard", subclass_id="college-lore", subclass_name="College of Lore",
        role="support-healing", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=False, primary_weapon=None,
        spell_package_id="college-lore", focus_item="musical-instrument",
        source_reference="Player's Handbook 2024: Bard, College of Lore, and Bard Spells",
    ),
    SubclassSpecialization(
        class_id="bard", subclass_id="college-valor", subclass_name="College of Valor",
        role="weapon-caster-hybrid", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=True, primary_weapon="rapier",
        spell_package_id="college-valor", focus_item="musical-instrument",
        source_reference="Player's Handbook 2024: Bard, College of Valor, and Bard Spells",
    ),
    SubclassSpecialization(
        class_id="bard", subclass_id="college-glamour", subclass_name="College of Glamour",
        role="control-caster", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=False, primary_weapon=None,
        spell_package_id="college-glamour", focus_item="musical-instrument",
        source_reference="Player's Handbook 2024: Bard, College of Glamour, and Bard Spells",
    ),
)
