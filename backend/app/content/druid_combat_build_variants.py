from __future__ import annotations

from typing import Literal

from app.content.combat_build_variants import (
    CombatBuildVariant,
    combat_build_variants_for,
    get_combat_build_variant,
)

DruidCombatRole = Literal["caster-damage", "healing", "wild-shape-melee"]
DruidVariantStatus = Literal["active", "planned"]
DruidCombatBuildVariant = CombatBuildVariant

DRUID_COMBAT_BUILD_VARIANTS: dict[str, DruidCombatBuildVariant] = {
    variant.id: variant for variant in combat_build_variants_for("druid")
}


def get_druid_combat_build_variant(variant_id: str) -> DruidCombatBuildVariant:
    return get_combat_build_variant("druid", variant_id)
