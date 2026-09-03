from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


DRUID_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="druid", subclass_id="circle-land", subclass_name="Circle of the Land",
        role="fire-caster", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="scale-mail", shield=True, primary_weapon="scimitar",
        spell_package_id="circle-land-arid", focus_item="druidic-focus",
        feature_choice_ids=("circle-land-arid", "elemental-fury-potent-spellcasting"),
        source_reference="Player's Handbook 2024: Druid, Circle of the Land, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="druid", subclass_id="circle-moon", subclass_name="Circle of the Moon",
        role="wild-shape-melee", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="scale-mail", shield=True, primary_weapon="scimitar",
        spell_package_id="circle-moon", focus_item="druidic-focus",
        feature_choice_ids=("moon-beast-form-package", "elemental-fury-primal-strike-cold"),
        source_reference="Player's Handbook 2024: Druid, Circle of the Moon, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="druid", subclass_id="circle-sea", subclass_name="Circle of the Sea",
        role="storm-controller", ability_priority=("wisdom", "charisma", "intelligence"),
        armor="scale-mail", shield=True, primary_weapon="scimitar",
        spell_package_id="circle-sea", focus_item="druidic-focus",
        feature_choice_ids=("elemental-fury-potent-spellcasting",),
        source_reference="Player's Handbook 2024: Druid, Circle of the Sea, Spells, and Equipment",
    ),
)
