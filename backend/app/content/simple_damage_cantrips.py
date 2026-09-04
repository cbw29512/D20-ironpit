from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.offensive_spell_effects import cantrip_damage_dice
from app.domain.actions import AbilityName, DamageTypeName
from app.domain.spells import SpellAttackAction, SpellModifierEffect, SpellSaveAction


@dataclass(frozen=True)
class DamageCantripSpec:
    id: str
    name: str
    resolution: Literal["attack", "save"]
    range_ft: int
    dice_size: int
    damage_type: DamageTypeName
    save_ability: AbilityName | None = None
    area_radius_ft: int | None = None
    on_hit_speed_reduction_ft: int = 0


SIMPLE_DAMAGE_CANTRIPS = {
    "acid-splash": DamageCantripSpec(
        "acid-splash", "Acid Splash", "save", 60, 6, "acid",
        save_ability="dexterity", area_radius_ft=5,
    ),
    "fire-bolt": DamageCantripSpec(
        "fire-bolt", "Fire Bolt", "attack", 120, 10, "fire",
    ),
    "poison-spray": DamageCantripSpec(
        "poison-spray", "Poison Spray", "attack", 30, 12, "poison",
    ),
    "ray-of-frost": DamageCantripSpec(
        "ray-of-frost", "Ray of Frost", "attack", 60, 8, "cold",
        on_hit_speed_reduction_ft=10,
    ),
    "sacred-flame": DamageCantripSpec(
        "sacred-flame", "Sacred Flame", "save", 60, 8, "radiant",
        save_ability="dexterity",
    ),
}


def _on_hit_effects(spec: DamageCantripSpec) -> list[SpellModifierEffect]:
    if not spec.on_hit_speed_reduction_ft:
        return []
    return [SpellModifierEffect(
        kind="speed",
        flat_bonus=-spec.on_hit_speed_reduction_ft,
        expires_at_end_of_target_turn=True,
    )]


def build_simple_damage_cantrip(
    cantrip_id: str,
    *,
    character_level: int,
    attack_bonus: int,
    save_dc: int,
) -> SpellAttackAction | SpellSaveAction:
    try:
        spec = SIMPLE_DAMAGE_CANTRIPS[cantrip_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported simple damage cantrip: {cantrip_id}.") from exc

    dice_count = cantrip_damage_dice(character_level)
    if spec.resolution == "attack":
        return SpellAttackAction(
            id=spec.id,
            name=spec.name,
            level=0,
            attack_kind="ranged",
            range_ft=spec.range_ft,
            attack_bonus=attack_bonus,
            damage_dice_count=dice_count,
            damage_dice_size=spec.dice_size,
            damage_type=spec.damage_type,
            on_hit_modifier_effects=_on_hit_effects(spec),
            animation=spec.id,
        )

    if spec.save_ability is None:
        raise ValueError(f"Save cantrip {spec.id} has no audited save ability.")
    return SpellSaveAction(
        id=spec.id,
        name=spec.name,
        level=0,
        range_ft=spec.range_ft,
        area_radius_ft=spec.area_radius_ft,
        save_ability=spec.save_ability,
        dc=save_dc,
        damage_dice_count=dice_count,
        damage_dice_size=spec.dice_size,
        damage_type=spec.damage_type,
        success_damage="none",
        animation=spec.id,
    )
