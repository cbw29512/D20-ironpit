from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DruidCombatRole = Literal["caster-damage", "healing", "wild-shape-melee"]
DruidVariantStatus = Literal["active", "planned"]


@dataclass(frozen=True)
class DruidCombatBuildVariant:
    id: str
    role: DruidCombatRole
    subclass_id: str | None
    status: DruidVariantStatus
    shared_progression_id: str = "druid-1-20"
    notes: str = ""


DRUID_COMBAT_BUILD_VARIANTS: dict[str, DruidCombatBuildVariant] = {
    "land-damage": DruidCombatBuildVariant(
        id="land-damage",
        role="caster-damage",
        subclass_id="circle-land",
        status="active",
        notes=(
            "Primary canonical Druid: spell-first damage/control overlay on the shared Druid 1-20 spine."
        ),
    ),
    "healer": DruidCombatBuildVariant(
        id="healer",
        role="healing",
        subclass_id=None,
        status="planned",
        notes=(
            "Future healing-first overlay. Reuse the shared Druid class spine; select and audit the legal 2024 "
            "subclass/spell package before runtime promotion rather than guessing it here."
        ),
    ),
    "moon-melee": DruidCombatBuildVariant(
        id="moon-melee",
        role="wild-shape-melee",
        subclass_id="circle-moon",
        status="planned",
        notes=(
            "Future Circle of the Moon melee overlay. Beast-form statistics, Wild Shape eligibility, replacement "
            "rules, resources, and tactical form policy require their own RAW audit before runtime promotion."
        ),
    ),
}


def get_druid_combat_build_variant(variant_id: str) -> DruidCombatBuildVariant:
    try:
        return DRUID_COMBAT_BUILD_VARIANTS[variant_id]
    except KeyError as exc:
        raise ValueError(f"Unknown Druid combat build variant: {variant_id}.") from exc
