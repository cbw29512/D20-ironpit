from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.content.offensive_spell_effects import cantrip_damage_dice
from app.domain.actions import AbilityName, DamageTypeName
from app.domain.spells import SpellAttackAction, SpellSaveAction


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
    "sacred-flame": DamageCantripSpec(
        "sacred-flame", "Sacred Flame", "save", 60, 8, "radiant",
        save_ability="dexterity",
    ),
}


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
