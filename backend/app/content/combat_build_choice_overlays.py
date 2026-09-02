from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.combat_build_variants import get_combat_build_variant
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
    "Graze": "graze-mastery", "Nick": "nick-mastery", "Sap": "sap-mastery",
    "Slow": "slow-mastery", "Vex": "vex-mastery",
}
_BUILD_TO_SUBCLASS = {
    "great-weapon": "champion",
    "dual-wield": "battle-master",
    "sword-shield": "eldritch-knight",
    "archer": "psi-warrior",
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
    notes: str = ""

    def __post_init__(self) -> None:
        get_combat_build_variant(self.class_id, self.build_id)


def _fighter_overlay(build_id: str) -> CombatBuildChoiceOverlay:
    spec = subclass_specialization(_BUILD_TO_SUBCLASS[build_id])
    masteries = spec.mastery_priority[:3]
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
        if capability == "slow-mastery":
            ignored.append(capability)
        elif capability and capability not in required:
            required.append(capability)
    return CombatBuildChoiceOverlay(
        class_id="fighter", build_id=build_id,
        primary_ability=spec.ability_priority[0], fighting_style=spec.fighting_style_priority[0] if spec.fighting_style_priority else None,
        armor=spec.armor, shield=spec.shield, primary_weapon=spec.primary_weapon,
        secondary_weapons=spec.secondary_weapons, weapon_masteries=masteries,
        required_capabilities=tuple(required), arena_ignored=tuple(ignored),
        notes=f"Compatibility view derived from {spec.subclass_name} specialization data.",
    )


FIGHTER_COMBAT_BUILD_CHOICES = {build_id: _fighter_overlay(build_id) for build_id in _BUILD_TO_SUBCLASS}


def get_combat_build_choice_overlay(class_id: str, build_id: str) -> CombatBuildChoiceOverlay:
    if class_id == "fighter":
        try:
            return FIGHTER_COMBAT_BUILD_CHOICES[build_id]
        except KeyError as exc:
            raise ValueError(f"Fighter combat build choices are not defined for {build_id}.") from exc
    raise ValueError(f"Combat build choices are not yet defined for class {class_id}.")


def maybe_combat_build_choice_overlay(class_id: str, build_id: str) -> CombatBuildChoiceOverlay | None:
    try:
        return get_combat_build_choice_overlay(class_id, build_id)
    except ValueError:
        get_combat_build_variant(class_id, build_id)
        return None
