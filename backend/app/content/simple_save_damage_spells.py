from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.domain.actions import AbilityName, DamageTypeName
from app.domain.areas import AreaGeometry
from app.domain.capabilities import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.spells import SpellSaveAction


@dataclass(frozen=True)
class SaveDamageSpellSpec:
    id: str
    name: str
    level: int
    range_ft: int
    save_ability: AbilityName
    dice_count: int
    dice_size: int
    damage_type: DamageTypeName
    success_damage: Literal["none", "half"] = "half"
    area_radius_ft: int | None = None
    area_shape: Literal["cube", "cone", "line"] | None = None
    area_size_ft: int | None = None
    damage_bonus: int = 0
    upcast_dice_per_level: int = 0


SIMPLE_SAVE_DAMAGE_SPELLS = {
    "thunderwave": SaveDamageSpellSpec(
        "thunderwave", "Thunderwave", 1, 15, "constitution", 2, 8, "thunder",
        area_shape="cube", area_size_ft=15, upcast_dice_per_level=1,
    ),
    "shatter": SaveDamageSpellSpec(
        "shatter", "Shatter", 2, 60, "constitution", 3, 8, "thunder",
        area_radius_ft=10, upcast_dice_per_level=1,
    ),
    "fireball": SaveDamageSpellSpec(
        "fireball", "Fireball", 3, 150, "dexterity", 8, 6, "fire",
        area_radius_ft=20, upcast_dice_per_level=1,
    ),
    "blight": SaveDamageSpellSpec(
        "blight", "Blight", 4, 30, "constitution", 8, 8, "necrotic",
        upcast_dice_per_level=1,
    ),
    "circle-of-death": SaveDamageSpellSpec(
        "circle-of-death", "Circle of Death", 6, 150, "constitution", 8, 8, "necrotic",
        area_radius_ft=60, upcast_dice_per_level=2,
    ),
    "disintegrate": SaveDamageSpellSpec(
        "disintegrate", "Disintegrate", 6, 60, "dexterity", 10, 6, "force",
        success_damage="none", damage_bonus=40,
    ),
    "finger-of-death": SaveDamageSpellSpec(
        "finger-of-death", "Finger of Death", 7, 60, "constitution", 7, 8, "necrotic",
        damage_bonus=30,
    ),
}


def _spec(spell_id: str) -> SaveDamageSpellSpec:
    try:
        return SIMPLE_SAVE_DAMAGE_SPELLS[spell_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported simple save-damage spell: {spell_id}.") from exc


def build_simple_save_damage_capability(
    spell_id: str,
    save_dc: int,
    *,
    resource_id: str | None = None,
) -> SaveCapabilityDefinition:
    """Build the source-neutral save/damage effect used by any caster access wrapper."""
    spec = _spec(spell_id)
    if spec.area_radius_ft is not None:
        raise ValueError(f"{spec.name} radius targeting still uses the shared spell-area wrapper.")
    area = None
    if spec.area_shape is not None:
        if spec.area_size_ft is None:
            raise ValueError(f"{spec.name} area shape requires a size.")
        area = AreaGeometry(shape=spec.area_shape, size_ft=spec.area_size_ft)
    return SaveCapabilityDefinition(
        id=spec.id, name=spec.name, save_ability=spec.save_ability, dc=save_dc,
        range_ft=spec.range_ft, area=area,
        damage=DiceSpec(count=spec.dice_count, size=spec.dice_size, bonus=spec.damage_bonus),
        damage_type=spec.damage_type, success_damage=spec.success_damage,
        resource_id=resource_id, resource_cost=1 if resource_id else None,
        animation=spec.id,
    )


def build_simple_save_damage_spell(spell_id: str, save_dc: int) -> SpellSaveAction:
    spec = _spec(spell_id)
    if spec.area_shape is not None:
        raise ValueError(f"{spec.name} uses non-radius geometry; use the shared save capability builder.")
    return SpellSaveAction(
        id=spec.id,
        name=spec.name,
        level=spec.level,
        range_ft=spec.range_ft,
        area_radius_ft=spec.area_radius_ft,
        save_ability=spec.save_ability,
        dc=save_dc,
        damage_dice_count=spec.dice_count,
        damage_dice_size=spec.dice_size,
        damage_bonus=spec.damage_bonus,
        damage_type=spec.damage_type,
        success_damage=spec.success_damage,
        upcast_dice_per_level=spec.upcast_dice_per_level,
        animation=spec.id,
    )
