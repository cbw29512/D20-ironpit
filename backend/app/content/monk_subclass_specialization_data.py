from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


MONK_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="monk", subclass_id="warrior-open-hand", subclass_name="Warrior of the Open Hand",
        role="unarmed-offense", ability_priority=("dexterity", "wisdom", "constitution"),
        armor=None, shield=False, primary_weapon=None,
        source_reference="SRD 5.2.1: Monk and Warrior of the Open Hand",
    ),
    SubclassSpecialization(
        class_id="monk", subclass_id="warrior-shadow", subclass_name="Warrior of Shadow",
        role="weapon-monk", ability_priority=("dexterity", "wisdom", "constitution"),
        armor=None, shield=False, primary_weapon="shortsword",
        source_reference="Player's Handbook 2024: Monk, Warrior of Shadow, and Equipment",
    ),
    SubclassSpecialization(
        class_id="monk", subclass_id="warrior-elements", subclass_name="Warrior of the Elements",
        role="defensive-mobile", ability_priority=("dexterity", "wisdom", "constitution"),
        armor=None, shield=False, primary_weapon=None,
        source_reference="Player's Handbook 2024: Monk and Warrior of the Elements",
    ),
)
