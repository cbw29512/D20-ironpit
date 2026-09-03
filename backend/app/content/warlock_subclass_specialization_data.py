from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


WARLOCK_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="warlock", subclass_id="fiend-patron", subclass_name="Fiend Patron",
        role="eldritch-blaster", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=False, primary_weapon=None,
        spell_package_id="fiend-patron", focus_item="arcane-focus",
        feature_choice_ids=("pact-of-the-tome",),
        source_reference="Player's Handbook 2024: Warlock, Fiend Patron, Invocations, and Warlock Spells",
    ),
    SubclassSpecialization(
        class_id="warlock", subclass_id="great-old-one-patron", subclass_name="Great Old One Patron",
        role="control-caster", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=False, primary_weapon=None,
        spell_package_id="great-old-one-patron", focus_item="arcane-focus",
        feature_choice_ids=("pact-of-the-tome",),
        source_reference="Player's Handbook 2024: Warlock, Great Old One Patron, Invocations, and Spells",
    ),
    SubclassSpecialization(
        class_id="warlock", subclass_id="celestial-patron", subclass_name="Celestial Patron",
        role="weapon-caster-hybrid", ability_priority=("charisma", "wisdom", "intelligence"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        spell_package_id="celestial-patron", focus_item="arcane-focus",
        feature_choice_ids=("pact-of-the-blade",),
        source_reference="Player's Handbook 2024: Warlock, Celestial Patron, Invocations, and Spells",
    ),
)
