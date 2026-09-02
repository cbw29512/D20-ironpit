from __future__ import annotations

from app.content.subclass_specialization_schema import SubclassSpecialization


BARBARIAN_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="barbarian", subclass_id="path-berserker", subclass_name="Path of the Berserker",
        role="two-handed", ability_priority=("strength", "constitution", "dexterity"),
        armor=None, shield=False, primary_weapon="greataxe", secondary_weapons=("battleaxe",),
        mastery_priority=("greataxe", "battleaxe", "greatsword", "longsword"),
        source_reference="Player's Handbook 2024: Barbarian, Path of the Berserker, and Equipment",
    ),
    SubclassSpecialization(
        class_id="barbarian", subclass_id="path-wild-heart", subclass_name="Path of the Wild Heart",
        role="weapon-shield", ability_priority=("strength", "constitution", "dexterity"),
        armor=None, shield=True, primary_weapon="battleaxe", secondary_weapons=("longsword",),
        mastery_priority=("battleaxe", "longsword", "greataxe", "greatsword"),
        feature_choice_ids=(
            "wild-heart-rage-bear", "wild-heart-aspect-elephant-athletics", "wild-heart-power-lion",
        ),
        source_reference="Player's Handbook 2024: Barbarian, Path of the Wild Heart, and Equipment",
    ),
    SubclassSpecialization(
        class_id="barbarian", subclass_id="path-zealot", subclass_name="Path of the Zealot",
        role="dual-wield", ability_priority=("strength", "constitution", "dexterity"),
        armor=None, shield=False, primary_weapon="shortsword", secondary_weapons=("scimitar",),
        mastery_priority=("shortsword", "scimitar", "greataxe", "battleaxe"),
        feature_choice_ids=("zealot-divine-fury-radiant",),
        source_reference="Player's Handbook 2024: Barbarian, Path of the Zealot, and Equipment",
    ),
)
