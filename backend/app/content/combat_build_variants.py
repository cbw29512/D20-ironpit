from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.hero_progressions import HERO_BY_CLASS

CombatBuildStatus = Literal["active", "planned"]


@dataclass(frozen=True)
class CombatBuildVariant:
    class_id: str
    id: str
    role: str
    status: CombatBuildStatus = "planned"
    required_subclass_id: str | None = None
    notes: str = ""

    @property
    def shared_progression_id(self) -> str:
        return f"{self.class_id}-1-20"

    @property
    def subclass_id(self) -> str | None:
        """Compatibility alias; non-None means this build requires that subclass."""
        return self.required_subclass_id


def _build(
    class_id: str,
    build_id: str,
    role: str,
    *,
    status: CombatBuildStatus = "planned",
    required_subclass_id: str | None = None,
    notes: str = "",
) -> CombatBuildVariant:
    return CombatBuildVariant(class_id, build_id, role, status, required_subclass_id, notes)


_VARIANTS = (
    _build(
        "fighter", "great-weapon", "two-handed-striker",
        notes="Shared GWF and Graze mechanics are supported; activation awaits a compiled build matching this overlay.",
    ),
    _build(
        "fighter", "sword-shield", "defender",
        notes="Shared Defense, Shield AC, and Sap mechanics are supported; activation awaits a compiled build matching this overlay.",
    ),
    _build("fighter", "archer", "ranged-striker"),
    _build("fighter", "dual-wield", "dual-wield-striker"),
    _build("barbarian", "great-weapon", "two-handed-striker", status="active"),
    _build("barbarian", "weapon-shield", "durable-melee"),
    _build("barbarian", "dual-wield", "dual-wield-striker"),
    _build("monk", "unarmed-offense", "unarmed-striker"),
    _build("monk", "weapon-monk", "weapon-striker"),
    _build("monk", "defensive-mobile", "defensive-mobile"),
    _build("paladin", "great-weapon", "smite-striker"),
    _build("paladin", "sword-shield", "protector"),
    _build("paladin", "support-healer", "support-healing"),
    _build("ranger", "archer", "ranged-striker"),
    _build("ranger", "dual-wield", "dual-wield-striker"),
    _build("ranger", "sword-shield", "durable-melee"),
    _build("rogue", "duelist", "finesse-duelist", status="active"),
    _build("rogue", "dual-wield", "dual-wield-finesse"),
    _build("rogue", "ranged", "crossbow-bow-sniper"),
    _build("wizard", "fire-damage", "fire-blaster"),
    _build("wizard", "frost-control", "cold-control"),
    _build("wizard", "mixed-arcane", "balanced-arcane"),
    _build("sorcerer", "fire-damage", "fire-blaster"),
    _build("sorcerer", "frost-control", "cold-control"),
    _build("sorcerer", "mixed-arcane", "balanced-arcane"),
    _build("warlock", "blaster", "eldritch-blaster"),
    _build("warlock", "controller", "control-caster"),
    _build("warlock", "blade-hybrid", "weapon-caster-hybrid"),
    _build("bard", "support-healer", "support-healing"),
    _build("bard", "controller", "control-caster"),
    _build("bard", "battle-bard", "weapon-caster-hybrid"),
    _build("cleric", "healer", "healing", status="active"),
    _build("cleric", "war-priest", "frontline-support"),
    _build("cleric", "divine-offense", "radiant-control"),
    _build(
        "druid", "land-damage", "caster-damage", status="active",
        required_subclass_id="circle-land",
    ),
    _build(
        "druid", "healer", "healing",
        notes="Healing-first spell/loadout overlay; subclass remains independently selectable.",
    ),
    _build(
        "druid", "moon-melee", "wild-shape-melee", required_subclass_id="circle-moon",
        notes="Requires a dedicated 2024 Wild Shape, beast-form, and tactical-form RAW audit before activation.",
    ),
)

COMBAT_BUILD_VARIANTS: dict[tuple[str, str], CombatBuildVariant] = {
    (variant.class_id, variant.id): variant for variant in _VARIANTS
}


def combat_build_variants_for(class_id: str) -> tuple[CombatBuildVariant, ...]:
    if class_id not in HERO_BY_CLASS:
        raise ValueError(f"Unknown canonical class: {class_id}.")
    return tuple(variant for variant in _VARIANTS if variant.class_id == class_id)


def get_combat_build_variant(class_id: str, build_id: str) -> CombatBuildVariant:
    try:
        return COMBAT_BUILD_VARIANTS[(class_id, build_id)]
    except KeyError as exc:
        raise ValueError(f"Unknown {class_id} combat build variant: {build_id}.") from exc
