from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


SORCERER_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="sorcerer", subclass_id="draconic-sorcery", subclass_name="Draconic Sorcery",
        role="fire-blaster", ability_priority=("charisma", "wisdom", "intelligence"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="draconic-sorcery", focus_item="arcane-focus",
        feature_choice_ids=("draconic-ancestor-red", "elemental-affinity-fire"),
        source_reference="Player's Handbook 2024: Sorcerer, Draconic Sorcery, and Sorcerer Spells",
    ),
    SubclassSpecialization(
        class_id="sorcerer", subclass_id="aberrant-sorcery", subclass_name="Aberrant Sorcery",
        role="control", ability_priority=("charisma", "wisdom", "intelligence"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="aberrant-sorcery", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Sorcerer, Aberrant Sorcery, and Sorcerer Spells",
    ),
    SubclassSpecialization(
        class_id="sorcerer", subclass_id="clockwork-sorcery", subclass_name="Clockwork Sorcery",
        role="balanced-arcane", ability_priority=("charisma", "wisdom", "intelligence"),
        armor=None, shield=False, primary_weapon=None,
        spell_package_id="clockwork-sorcery", focus_item="arcane-focus",
        source_reference="Player's Handbook 2024: Sorcerer, Clockwork Sorcery, and Sorcerer Spells",
    ),
)
