from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.combat_build_variants import combat_build_variants_for, get_combat_build_variant
from app.content.subclass_specializations import subclass_specialization
from app.content.weapon_catalog import build_weapon

AbilityFocus = Literal["strength", "dexterity", "wisdom", "intelligence", "charisma"]

_STYLE_CAPABILITY = {
    "Archery": "archery-style",
    "Defense": "defense-style",
    "Great Weapon Fighting": "great-weapon-fighting",
    "Two-Weapon Fighting": "two-weapon-fighting",
}
_MASTERY_CAPABILITY = {
    "Cleave": "cleave-mastery", "Graze": "graze-mastery", "Nick": "nick-mastery",
    "Sap": "sap-mastery", "Slow": "slow-mastery", "Topple": "topple-mastery",
    "Vex": "vex-mastery",
}
_MASTERY_LIMIT = {
    "fighter": 3, "barbarian": 2, "monk": 0,
    "paladin": 2, "ranger": 2, "rogue": 2, "wizard": 0,
    "sorcerer": 0, "warlock": 0, "bard": 0,
}


@dataclass(frozen=True)
class CombatBuildChoiceOverlay:
    class_id: str
    build_id: str
    primary_ability: AbilityFocus
    fighting_style: str | None = None
    armor: str | None = None
    shield: bool = False
    primary_weapon: str | None = None
    secondary_weapons: tuple[str, ...] = ()
    weapon_masteries: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    spell_package_id: str | None = None
    focus_item: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        get_combat_build_variant(self.class_id, self.build_id)


def _build_overlay(class_id: str, build_id: str) -> CombatBuildChoiceOverlay:
    variant = get_combat_build_variant(class_id, build_id)
    if variant.required_subclass_id is None:
        raise ValueError(f"Specialized build {class_id}/{build_id} requires a subclass owner.")
    spec = subclass_specialization(variant.required_subclass_id)
    if spec.class_id != class_id:
        raise ValueError(f"Build {class_id}/{build_id} points to a {spec.class_id} specialization.")
    masteries = spec.mastery_priority[:_MASTERY_LIMIT[class_id]]
    required: list[str] = []
    ignored: list[str] = []
    if spec.fighting_style_priority:
        capability = _STYLE_CAPABILITY.get(spec.fighting_style_priority[0])
        if capability:
            required.append(capability)
    if spec.shield:
        required.append("shield-ac")
    for weapon_id in (spec.primary_weapon, *spec.secondary_weapons):
        if weapon_id is None or weapon_id not in masteries:
            continue
        mastery = build_weapon(weapon_id).mastery_property
        capability = _MASTERY_CAPABILITY.get(mastery or "")
        if capability is None:
            raise ValueError(f"No shared capability maps weapon mastery {mastery!r}.")
        if capability == "slow-mastery":
            ignored.append(capability)
        elif capability not in required:
            required.append(capability)
    return CombatBuildChoiceOverlay(
        class_id=class_id, build_id=build_id,
        primary_ability=spec.ability_priority[0],
        fighting_style=spec.fighting_style_priority[0] if spec.fighting_style_priority else None,
        armor=spec.armor, shield=spec.shield, primary_weapon=spec.primary_weapon,
        secondary_weapons=spec.secondary_weapons, weapon_masteries=masteries,
        required_capabilities=tuple(required), arena_ignored=tuple(ignored),
        notes=f"Compatibility view derived from {spec.subclass_name} specialization data.",
        spell_package_id=spec.spell_package_id, focus_item=spec.focus_item,
    )


COMBAT_BUILD_CHOICE_OVERLAYS = {
    (class_id, variant.id): _build_overlay(class_id, variant.id)
    for class_id in _MASTERY_LIMIT
    for variant in combat_build_variants_for(class_id)
}


def _choices_for_class(class_id: str) -> dict[str, CombatBuildChoiceOverlay]:
    return {
        build_id: overlay
        for (owner_class_id, build_id), overlay in COMBAT_BUILD_CHOICE_OVERLAYS.items()
        if owner_class_id == class_id
    }


FIGHTER_COMBAT_BUILD_CHOICES = _choices_for_class("fighter")
BARBARIAN_COMBAT_BUILD_CHOICES = _choices_for_class("barbarian")
MONK_COMBAT_BUILD_CHOICES = _choices_for_class("monk")
PALADIN_COMBAT_BUILD_CHOICES = _choices_for_class("paladin")
RANGER_COMBAT_BUILD_CHOICES = _choices_for_class("ranger")
ROGUE_COMBAT_BUILD_CHOICES = _choices_for_class("rogue")
WIZARD_COMBAT_BUILD_CHOICES = _choices_for_class("wizard")
SORCERER_COMBAT_BUILD_CHOICES = _choices_for_class("sorcerer")
WARLOCK_COMBAT_BUILD_CHOICES = _choices_for_class("warlock")
BARD_COMBAT_BUILD_CHOICES = _choices_for_class("bard")


def get_combat_build_choice_overlay(class_id: str, build_id: str) -> CombatBuildChoiceOverlay:
    try:
        return COMBAT_BUILD_CHOICE_OVERLAYS[(class_id, build_id)]
    except KeyError as exc:
        raise ValueError(f"Combat build choices are not defined for {class_id}/{build_id}.") from exc


def maybe_combat_build_choice_overlay(class_id: str, build_id: str) -> CombatBuildChoiceOverlay | None:
    try:
        return get_combat_build_choice_overlay(class_id, build_id)
    except ValueError:
        get_combat_build_variant(class_id, build_id)
        return None
