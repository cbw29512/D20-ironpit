from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.models import DamageType, WeaponAttackKind

logger = logging.getLogger(__name__)


class Weapon2014Definition(BaseModel):
    id: str
    name: str
    category: Literal["simple", "martial"]
    attack_kind: WeaponAttackKind
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int | None = Field(default=None, ge=2, le=100)
    fixed_damage: int | None = Field(default=None, ge=0)
    damage_type: DamageType | None = None
    cost: str
    weight_lb: float | None = Field(default=None, ge=0)
    properties: tuple[str, ...] = ()
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    versatile_dice_count: int | None = Field(default=None, ge=1, le=20)
    versatile_dice_size: int | None = Field(default=None, ge=2, le=100)

    @model_validator(mode="after")
    def validate_damage_modes(self) -> "Weapon2014Definition":
        if self.dice_count and self.dice_size is None:
            raise ValueError("Rolled weapon damage requires a die size.")
        if (self.dice_count or self.fixed_damage) and self.damage_type is None:
            raise ValueError("Damaging weapons require a damage type.")
        if (self.versatile_dice_count is None) != (self.versatile_dice_size is None):
            raise ValueError("Versatile damage requires both count and size.")
        return self


def _w(
    weapon_id: str,
    name: str,
    category: Literal["simple", "martial"],
    attack_kind: WeaponAttackKind,
    dice_count: int,
    dice_size: int | None,
    damage_type: DamageType | None,
    cost: str,
    weight_lb: float | None,
    properties: tuple[str, ...] = (),
    *,
    fixed_damage: int | None = None,
    normal_range_ft: int | None = None,
    long_range_ft: int | None = None,
    versatile: tuple[int, int] | None = None,
) -> Weapon2014Definition:
    try:
        versatile_count, versatile_size = versatile or (None, None)
        return Weapon2014Definition(
            id=weapon_id, name=name, category=category, attack_kind=attack_kind,
            dice_count=dice_count, dice_size=dice_size, fixed_damage=fixed_damage,
            damage_type=damage_type, cost=cost, weight_lb=weight_lb, properties=properties,
            normal_range_ft=normal_range_ft, long_range_ft=long_range_ft,
            versatile_dice_count=versatile_count, versatile_dice_size=versatile_size,
        )
    except Exception:
        logger.exception("Invalid 2014 weapon definition: %s", weapon_id)
        raise


M = WeaponAttackKind.MELEE
R = WeaponAttackKind.RANGED
B = DamageType.BLUDGEONING
P = DamageType.PIERCING
S = DamageType.SLASHING

_WEAPONS_2014 = {
    "club": _w("club", "Club", "simple", M, 1, 4, B, "1 sp", 2, ("light",)),
    "dagger": _w("dagger", "Dagger", "simple", M, 1, 4, P, "2 gp", 1, ("finesse", "light", "thrown"), normal_range_ft=20, long_range_ft=60),
    "greatclub": _w("greatclub", "Greatclub", "simple", M, 1, 8, B, "2 sp", 10, ("two_handed",)),
    "handaxe": _w("handaxe", "Handaxe", "simple", M, 1, 6, S, "5 gp", 2, ("light", "thrown"), normal_range_ft=20, long_range_ft=60),
    "javelin": _w("javelin", "Javelin", "simple", M, 1, 6, P, "5 sp", 2, ("thrown",), normal_range_ft=30, long_range_ft=120),
    "light-hammer": _w("light-hammer", "Light Hammer", "simple", M, 1, 4, B, "2 gp", 2, ("light", "thrown"), normal_range_ft=20, long_range_ft=60),
    "mace": _w("mace", "Mace", "simple", M, 1, 6, B, "5 gp", 4),
    "quarterstaff": _w("quarterstaff", "Quarterstaff", "simple", M, 1, 6, B, "2 sp", 4, ("versatile",), versatile=(1, 8)),
    "sickle": _w("sickle", "Sickle", "simple", M, 1, 4, S, "1 gp", 2, ("light",)),
    "spear": _w("spear", "Spear", "simple", M, 1, 6, P, "1 gp", 3, ("thrown", "versatile"), normal_range_ft=20, long_range_ft=60, versatile=(1, 8)),
    "light-crossbow": _w("light-crossbow", "Crossbow, Light", "simple", R, 1, 8, P, "25 gp", 5, ("ammunition", "loading", "two_handed"), normal_range_ft=80, long_range_ft=320),
    "dart": _w("dart", "Dart", "simple", R, 1, 4, P, "5 cp", 0.25, ("finesse", "thrown"), normal_range_ft=20, long_range_ft=60),
    "shortbow": _w("shortbow", "Shortbow", "simple", R, 1, 6, P, "25 gp", 2, ("ammunition", "two_handed"), normal_range_ft=80, long_range_ft=320),
    "sling": _w("sling", "Sling", "simple", R, 1, 4, B, "1 sp", None, ("ammunition",), normal_range_ft=30, long_range_ft=120),
    "battleaxe": _w("battleaxe", "Battleaxe", "martial", M, 1, 8, S, "10 gp", 4, ("versatile",), versatile=(1, 10)),
    "flail": _w("flail", "Flail", "martial", M, 1, 8, B, "10 gp", 2),
    "glaive": _w("glaive", "Glaive", "martial", M, 1, 10, S, "20 gp", 6, ("heavy", "reach", "two_handed")),
    "greataxe": _w("greataxe", "Greataxe", "martial", M, 1, 12, S, "30 gp", 7, ("heavy", "two_handed")),
    "greatsword": _w("greatsword", "Greatsword", "martial", M, 2, 6, S, "50 gp", 6, ("heavy", "two_handed")),
    "halberd": _w("halberd", "Halberd", "martial", M, 1, 10, S, "20 gp", 6, ("heavy", "reach", "two_handed")),
    "lance": _w("lance", "Lance", "martial", M, 1, 12, P, "10 gp", 6, ("reach", "special")),
    "longsword": _w("longsword", "Longsword", "martial", M, 1, 8, S, "15 gp", 3, ("versatile",), versatile=(1, 10)),
    "maul": _w("maul", "Maul", "martial", M, 2, 6, B, "10 gp", 10, ("heavy", "two_handed")),
    "morningstar": _w("morningstar", "Morningstar", "martial", M, 1, 8, P, "15 gp", 4),
    "pike": _w("pike", "Pike", "martial", M, 1, 10, P, "5 gp", 18, ("heavy", "reach", "two_handed")),
    "rapier": _w("rapier", "Rapier", "martial", M, 1, 8, P, "25 gp", 2, ("finesse",)),
    "scimitar": _w("scimitar", "Scimitar", "martial", M, 1, 6, S, "25 gp", 3, ("finesse", "light")),
    "shortsword": _w("shortsword", "Shortsword", "martial", M, 1, 6, P, "10 gp", 2, ("finesse", "light")),
    "trident": _w("trident", "Trident", "martial", M, 1, 6, P, "5 gp", 4, ("thrown", "versatile"), normal_range_ft=20, long_range_ft=60, versatile=(1, 8)),
    "war-pick": _w("war-pick", "War Pick", "martial", M, 1, 8, P, "5 gp", 2),
    "warhammer": _w("warhammer", "Warhammer", "martial", M, 1, 8, B, "15 gp", 2, ("versatile",), versatile=(1, 10)),
    "whip": _w("whip", "Whip", "martial", M, 1, 4, S, "2 gp", 3, ("finesse", "reach")),
    "blowgun": _w("blowgun", "Blowgun", "martial", R, 0, None, P, "10 gp", 1, ("ammunition", "loading"), fixed_damage=1, normal_range_ft=25, long_range_ft=100),
    "hand-crossbow": _w("hand-crossbow", "Crossbow, Hand", "martial", R, 1, 6, P, "75 gp", 3, ("ammunition", "light", "loading"), normal_range_ft=30, long_range_ft=120),
    "heavy-crossbow": _w("heavy-crossbow", "Crossbow, Heavy", "martial", R, 1, 10, P, "50 gp", 18, ("ammunition", "heavy", "loading", "two_handed"), normal_range_ft=100, long_range_ft=400),
    "longbow": _w("longbow", "Longbow", "martial", R, 1, 8, P, "50 gp", 2, ("ammunition", "heavy", "two_handed"), normal_range_ft=150, long_range_ft=600),
    "net": _w("net", "Net", "martial", R, 0, None, None, "1 gp", 3, ("special", "thrown"), normal_range_ft=5, long_range_ft=15),
}


def build_weapon_2014(weapon_id: str) -> Weapon2014Definition:
    try:
        return _WEAPONS_2014[weapon_id].model_copy(deep=True)
    except KeyError as exc:
        logger.warning("Unknown 2014 weapon requested: %s", weapon_id)
        raise ValueError(f"Unknown 2014 weapon: {weapon_id}.") from exc


def official_weapon_ids_2014() -> tuple[str, ...]:
    try:
        return tuple(_WEAPONS_2014)
    except Exception:
        logger.exception("Failed to enumerate the 2014 weapon catalog.")
        raise


def select_damage_mode_2014(weapon_id: str, *, second_hand_free: bool) -> tuple[int, int | None, int | None]:
    try:
        weapon = build_weapon_2014(weapon_id)
        if "two_handed" in weapon.properties and not second_hand_free:
            raise ValueError(f"{weapon.name} requires two hands to attack.")
        if second_hand_free and weapon.versatile_dice_size is not None:
            return weapon.versatile_dice_count or 1, weapon.versatile_dice_size, None
        return weapon.dice_count, weapon.dice_size, weapon.fixed_damage
    except Exception:
        logger.exception("Failed to resolve 2014 weapon damage mode: %s", weapon_id)
        raise
