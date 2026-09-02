from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.combat_build_variants import get_combat_build_variant

AbilityFocus = Literal["strength", "dexterity", "wisdom", "intelligence", "charisma"]


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


FIGHTER_COMBAT_BUILD_CHOICES: dict[str, CombatBuildChoiceOverlay] = {
    "great-weapon": CombatBuildChoiceOverlay(
        class_id="fighter",
        build_id="great-weapon",
        primary_ability="strength",
        fighting_style="Great Weapon Fighting",
        armor="chain-mail",
        primary_weapon="greatsword",
        secondary_weapons=("shortbow",),
        weapon_masteries=("greatsword", "javelin", "flail"),
        required_capabilities=("great-weapon-fighting", "graze-mastery"),
        notes="Damage-first two-handed Fighter. Uses the shared Fighter/Champion progression.",
    ),
    "sword-shield": CombatBuildChoiceOverlay(
        class_id="fighter",
        build_id="sword-shield",
        primary_ability="strength",
        fighting_style="Defense",
        armor="chain-mail",
        shield=True,
        primary_weapon="longsword",
        secondary_weapons=("shortbow",),
        weapon_masteries=("longsword", "javelin", "flail"),
        required_capabilities=("defense-style", "shield-ac", "sap-mastery"),
        notes="Durable defender bought from the Fighter gold option; no separate Fighter progression.",
    ),
    "archer": CombatBuildChoiceOverlay(
        class_id="fighter",
        build_id="archer",
        primary_ability="dexterity",
        fighting_style="Archery",
        armor="studded-leather",
        primary_weapon="longbow",
        secondary_weapons=("shortsword", "scimitar"),
        weapon_masteries=("longbow", "shortsword", "scimitar"),
        required_capabilities=("archery-style", "vex-mastery", "nick-mastery"),
        arena_ignored=("slow-mastery",),
        notes="Ranged-first Fighter; Slow is explicitly ignored when it cannot change an Iron Pit outcome.",
    ),
    "dual-wield": CombatBuildChoiceOverlay(
        class_id="fighter",
        build_id="dual-wield",
        primary_ability="dexterity",
        fighting_style="Two-Weapon Fighting",
        armor="studded-leather",
        primary_weapon="shortsword",
        secondary_weapons=("scimitar", "longbow"),
        weapon_masteries=("shortsword", "scimitar", "longbow"),
        required_capabilities=("two-weapon-fighting", "nick-mastery", "vex-mastery"),
        arena_ignored=("slow-mastery",),
        notes="Vex Shortsword into Nick Scimitar dual-wield package from the legal Fighter starting-equipment option B.",
    ),
}


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
