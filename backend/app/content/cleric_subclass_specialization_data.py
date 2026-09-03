from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


CLERIC_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="cleric", subclass_id="life-domain", subclass_name="Life Domain",
        role="support-healing", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="chain-mail", shield=True, primary_weapon="mace",
        spell_package_id="life-domain", focus_item="holy-symbol",
        feature_choice_ids=("blessed-strikes-potent-spellcasting",),
        source_reference="Player's Handbook 2024: Cleric, Life Domain, Cleric Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="cleric", subclass_id="light-domain", subclass_name="Light Domain",
        role="radiant-control", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="chain-mail", shield=False, primary_weapon=None,
        spell_package_id="light-domain", focus_item="holy-symbol",
        feature_choice_ids=("blessed-strikes-potent-spellcasting",),
        source_reference="Player's Handbook 2024: Cleric, Light Domain, Cleric Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="cleric", subclass_id="war-domain", subclass_name="War Domain",
        role="frontline-support", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        spell_package_id="war-domain", focus_item="holy-symbol",
        feature_choice_ids=("blessed-strikes-divine-strike-radiant",),
        source_reference="Player's Handbook 2024: Cleric, War Domain, Cleric Spells, and Equipment",
    ),
)
