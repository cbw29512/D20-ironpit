from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubclassSpecialization:
    class_id: str
    subclass_id: str
    subclass_name: str
    role: str
    ability_priority: tuple[str, ...]
    armor: str | None
    shield: bool
    primary_weapon: str | None
    source_reference: str
    secondary_weapons: tuple[str, ...] = ()
    fighting_style_priority: tuple[str, ...] = ()
    mastery_priority: tuple[str, ...] = ()
    spell_package_id: str | None = None
    focus_item: str | None = None
    feature_choice_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_reference.strip():
            raise ValueError(f"Subclass specialization {self.subclass_id!r} requires a source reference.")
        if self.primary_weapon and self.mastery_priority and self.primary_weapon not in self.mastery_priority:
            raise ValueError(f"Primary weapon {self.primary_weapon!r} must be in the mastery priority.")
        if self.shield and self.primary_weapon is None:
            raise ValueError(f"Shield specialization {self.subclass_id!r} requires a one-handed weapon.")


FIGHTER_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="fighter", subclass_id="champion", subclass_name="Champion",
        role="two-handed", ability_priority=("strength", "constitution", "dexterity"),
        armor="chain-mail", shield=False, primary_weapon="greatsword",
        secondary_weapons=("shortbow",),
        fighting_style_priority=("Great Weapon Fighting", "Defense"),
        mastery_priority=("greatsword", "shortbow", "longsword", "shortsword", "scimitar"),
        source_reference="Player's Handbook 2024: Fighter, Champion, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="battle-master", subclass_name="Battle Master",
        role="dual-wield", ability_priority=("dexterity", "constitution", "wisdom"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        secondary_weapons=("scimitar", "longbow"),
        fighting_style_priority=("Two-Weapon Fighting",),
        mastery_priority=("shortsword", "scimitar", "longbow", "longsword", "greatsword"),
        source_reference="Player's Handbook 2024: Fighter, Battle Master, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="eldritch-knight", subclass_name="Eldritch Knight",
        role="sword-shield", ability_priority=("strength", "intelligence", "constitution"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        secondary_weapons=("shortbow",),
        fighting_style_priority=("Defense",),
        mastery_priority=("longsword", "shortbow", "greatsword", "shortsword", "scimitar"),
        spell_package_id="eldritch-knight",
        source_reference="Player's Handbook 2024: Fighter, Eldritch Knight, Spells, and Equipment",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="psi-warrior", subclass_name="Psi Warrior",
        role="ranged", ability_priority=("dexterity", "intelligence", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="longbow",
        secondary_weapons=("shortsword", "scimitar"),
        fighting_style_priority=("Archery",),
        mastery_priority=("longbow", "shortsword", "scimitar", "longsword", "greatsword"),
        source_reference="Player's Handbook 2024: Fighter, Psi Warrior, and Equipment",
    ),
)


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


def _specialization_registry() -> dict[str, SubclassSpecialization]:
    registry: dict[str, SubclassSpecialization] = {}
    for item in (*FIGHTER_SPECIALIZATIONS, *BARBARIAN_SPECIALIZATIONS):
        if item.subclass_id in registry:
            raise ValueError(f"Duplicate subclass specialization: {item.subclass_id}.")
        registry[item.subclass_id] = item
    return registry


_SPECIALIZATIONS = _specialization_registry()


def subclass_specialization(subclass_id: str) -> SubclassSpecialization:
    try:
        return _SPECIALIZATIONS[subclass_id]
    except KeyError as exc:
        raise ValueError(f"No audited combat specialization for subclass: {subclass_id}.") from exc


def specializations_for_class(class_id: str) -> tuple[SubclassSpecialization, ...]:
    return tuple(item for item in _SPECIALIZATIONS.values() if item.class_id == class_id)
