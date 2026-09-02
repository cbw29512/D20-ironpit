from __future__ import annotations

from app.domain.models import DamageType, Weapon, WeaponAttackKind


def _melee(
    weapon_id: str,
    name: str,
    dice_count: int,
    dice_size: int,
    damage_type: DamageType,
    mastery: str,
    **properties: bool,
) -> Weapon:
    return Weapon(
        id=weapon_id,
        name=name,
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=dice_count,
        dice_size=dice_size,
        damage_type=damage_type,
        animation="heavy-slash" if properties.get("heavy") else "slash",
        reach_ft=5,
        mastery_property=mastery,
        **properties,
    )


def _ranged(
    weapon_id: str,
    name: str,
    dice_size: int,
    normal_range_ft: int,
    long_range_ft: int,
    mastery: str,
    **properties: bool,
) -> Weapon:
    return Weapon(
        id=weapon_id,
        name=name,
        attack_kind=WeaponAttackKind.RANGED,
        dice_count=1,
        dice_size=dice_size,
        damage_type=DamageType.PIERCING,
        animation="projectile",
        normal_range_ft=normal_range_ft,
        long_range_ft=long_range_ft,
        projectile="arrow",
        mastery_property=mastery,
        **properties,
    )


_WEAPONS = {
    "greatsword": _melee(
        "greatsword", "Greatsword", 2, 6, DamageType.SLASHING, "Graze",
        heavy=True, two_handed=True,
    ),
    "longsword": _melee(
        "longsword", "Longsword", 1, 8, DamageType.SLASHING, "Sap",
        versatile=True,
    ),
    "scimitar": _melee(
        "scimitar", "Scimitar", 1, 6, DamageType.SLASHING, "Nick",
        finesse=True, light=True,
    ),
    "shortsword": _melee(
        "shortsword", "Shortsword", 1, 6, DamageType.PIERCING, "Vex",
        finesse=True, light=True,
    ),
    "longbow": _ranged(
        "longbow", "Longbow", 8, 150, 600, "Slow",
        heavy=True, two_handed=True,
    ),
    "shortbow": _ranged(
        "shortbow", "Shortbow", 6, 80, 320, "Vex",
        two_handed=True,
    ),
}


def build_weapon(weapon_id: str) -> Weapon:
    try:
        return _WEAPONS[weapon_id].model_copy(deep=True)
    except KeyError as exc:
        raise ValueError(f"Unknown audited weapon: {weapon_id}.") from exc


def audited_weapon_ids() -> tuple[str, ...]:
    return tuple(_WEAPONS)
