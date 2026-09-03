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
        "fighter", "great-weapon", "two-handed-striker", required_subclass_id="champion",
        notes="Champion specialization: Greatsword + Great Weapon Fighting; shared mechanics stay generic.",
    ),
    _build(
        "fighter", "sword-shield", "defender", required_subclass_id="eldritch-knight",
        notes="Eldritch Knight specialization: Longsword + Shield; activation awaits audited subclass/spells.",
    ),
    _build(
        "fighter", "archer", "ranged-striker", required_subclass_id="psi-warrior",
        notes="Psi Warrior specialization: ranged weapon + Archery; activation awaits audited subclass features.",
    ),
    _build(
        "fighter", "dual-wield", "dual-wield-striker", required_subclass_id="battle-master",
        notes="Battle Master specialization: Shortsword + Scimitar + Two-Weapon Fighting; maneuvers remain fail-closed.",
    ),
    _build("barbarian", "great-weapon", "two-handed-striker", required_subclass_id="path-berserker"),
    _build("barbarian", "weapon-shield", "durable-melee", required_subclass_id="path-wild-heart"),
    _build("barbarian", "dual-wield", "dual-wield-striker", required_subclass_id="path-zealot"),
    _build("monk", "unarmed-offense", "unarmed-striker", required_subclass_id="warrior-open-hand"),
    _build("monk", "weapon-monk", "weapon-striker", required_subclass_id="warrior-shadow"),
    _build("monk", "defensive-mobile", "defensive-mobile", required_subclass_id="warrior-elements"),
    _build("paladin", "great-weapon", "smite-striker", required_subclass_id="oath-vengeance"),
    _build("paladin", "sword-shield", "protector", required_subclass_id="oath-devotion"),
    _build("paladin", "support-healer", "support-healing", required_subclass_id="oath-ancients"),
    _build("ranger", "archer", "ranged-striker", required_subclass_id="gloom-stalker"),
    _build("ranger", "dual-wield", "dual-wield-striker", required_subclass_id="beastmaster"),
    _build("ranger", "sword-shield", "durable-melee", required_subclass_id="hunter"),
    _build("rogue", "duelist", "finesse-duelist"),
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
    _build("cleric", "healer", "healing"),
    _build("cleric", "war-priest", "frontline-support"),
    _build("cleric", "divine-offense", "radiant-control"),
    _build(
        "druid", "land-damage", "caster-damage", required_subclass_id="circle-land",
        notes="Canonical Land Druid progression is separate; named build activation awaits a compiled build overlay.",
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
