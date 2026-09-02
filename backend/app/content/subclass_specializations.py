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
    secondary_weapons: tuple[str, ...] = ()
    fighting_style_priority: tuple[str, ...] = ()
    mastery_priority: tuple[str, ...] = ()
    spell_package_id: str | None = None
    focus_item: str | None = None


FIGHTER_SPECIALIZATIONS = (
    SubclassSpecialization(
        class_id="fighter", subclass_id="champion", subclass_name="Champion",
        role="two-handed", ability_priority=("strength", "constitution", "dexterity"),
        armor="chain-mail", shield=False, primary_weapon="greatsword",
        secondary_weapons=("shortbow",),
        fighting_style_priority=("Great Weapon Fighting", "Defense"),
        mastery_priority=("greatsword", "shortbow", "longsword", "shortsword", "scimitar"),
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="battle-master", subclass_name="Battle Master",
        role="dual-wield", ability_priority=("dexterity", "constitution", "wisdom"),
        armor="studded-leather", shield=False, primary_weapon="shortsword",
        secondary_weapons=("scimitar", "longbow"),
        fighting_style_priority=("Two-Weapon Fighting",),
        mastery_priority=("shortsword", "scimitar", "longbow", "longsword", "greatsword"),
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="eldritch-knight", subclass_name="Eldritch Knight",
        role="sword-shield", ability_priority=("strength", "intelligence", "constitution"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        secondary_weapons=("shortbow",),
        fighting_style_priority=("Defense",),
        mastery_priority=("longsword", "shortbow", "greatsword", "shortsword", "scimitar"),
        spell_package_id="eldritch-knight",
    ),
    SubclassSpecialization(
        class_id="fighter", subclass_id="psi-warrior", subclass_name="Psi Warrior",
        role="ranged", ability_priority=("dexterity", "intelligence", "constitution"),
        armor="studded-leather", shield=False, primary_weapon="longbow",
        secondary_weapons=("shortsword", "scimitar"),
        fighting_style_priority=("Archery",),
        mastery_priority=("longbow", "shortsword", "scimitar", "longsword", "greatsword"),
    ),
)


_SPECIALIZATIONS = {item.subclass_id: item for item in FIGHTER_SPECIALIZATIONS}


def subclass_specialization(subclass_id: str) -> SubclassSpecialization:
    try:
        return _SPECIALIZATIONS[subclass_id]
    except KeyError as exc:
        raise ValueError(f"No audited combat specialization for subclass: {subclass_id}.") from exc


def specializations_for_class(class_id: str) -> tuple[SubclassSpecialization, ...]:
    return tuple(item for item in _SPECIALIZATIONS.values() if item.class_id == class_id)
