from __future__ import annotations

import logging

from app.content.monster_equipment import build_monster_visual
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _attack(
    attack_id: str, name: str, kind: WeaponAttackKind, bonus: int,
    dice_count: int, dice_size: int, damage_bonus: int, *,
    normal: int | None = None, long: int | None = None,
    poison_dice: tuple[int, int] | None = None,
) -> WeaponAttack:
    try:
        damage_type = DamageType.PIERCING if name in {"Dagger", "Longbow"} else DamageType.SLASHING
        weapon = Weapon(
            id=attack_id, name=name, attack_kind=kind, dice_count=dice_count,
            dice_size=dice_size, damage_type=damage_type,
            animation="projectile" if kind == WeaponAttackKind.RANGED else "slash",
            normal_range_ft=normal, long_range_ft=long,
            projectile="arrow" if name == "Longbow" else "dagger" if kind == WeaponAttackKind.RANGED else None,
        )
        extras = [] if poison_dice is None else [OnHitDamage(
            source="Poison", dice_count=poison_dice[0], dice_size=poison_dice[1],
            damage_type=DamageType.POISON,
        )]
        return WeaponAttack(
            id=attack_id, weapon=weapon, attack_bonus=bonus,
            damage_bonus=damage_bonus, on_hit_damage=extras,
        )
    except Exception as exc:
        logger.exception("Failed to build expansion attack %s.", attack_id)
        raise RuntimeError(f"Expansion attack {attack_id} could not be created.") from exc


def _daggers(prefix: str) -> tuple[WeaponAttack, WeaponAttack]:
    try:
        return (
            _attack(f"{prefix}-dagger-melee", "Dagger", WeaponAttackKind.MELEE, 4, 1, 4, 2),
            _attack(f"{prefix}-dagger-ranged", "Dagger", WeaponAttackKind.RANGED, 4, 1, 4, 2, normal=20, long=60),
        )
    except Exception as exc:
        logger.exception("Failed to build dagger pair for %s.", prefix)
        raise RuntimeError(f"Dagger pair for {prefix} could not be created.") from exc


def _monster(**kwargs) -> CombatantTemplate:
    try:
        return CombatantTemplate(kind="monster", **kwargs)
    except Exception as exc:
        monster_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build expansion monster %s.", monster_id)
        raise RuntimeError(f"Expansion monster {monster_id} could not be created.") from exc


def build_goblin_minion() -> CombatantTemplate:
    melee, ranged = _daggers("goblin-minion")
    return _monster(
        id="srd-goblin-minion", name="Goblin Minion", archetype="Goblin Minion",
        challenge_rating="1/8", size="small", armor_class=12, max_hp=7,
        speed_ft=30, initiative_bonus=2, weapon_attack=melee,
        alternate_weapon_attacks=[ranged], visual=build_monster_visual("clothes", "dagger", "goblinoid"),
        source="SRD 5.2.1 p. 290 Goblin Minion",
    )


def build_kobold_warrior() -> CombatantTemplate:
    melee, ranged = _daggers("kobold-warrior")
    return _monster(
        id="srd-kobold-warrior", name="Kobold Warrior", archetype="Kobold Warrior",
        challenge_rating="1/8", size="small", armor_class=14, max_hp=7,
        speed_ft=30, initiative_bonus=2, weapon_attack=melee,
        alternate_weapon_attacks=[ranged], combat_traits=[CombatTrait.PACK_TACTICS],
        visual=build_monster_visual("natural", "dagger", "kobold"),
        source="SRD 5.2.1 p. 302 Kobold Warrior",
    )


def build_hobgoblin_warrior() -> CombatantTemplate:
    longsword = _attack("hobgoblin-longsword", "Longsword", WeaponAttackKind.MELEE, 3, 2, 10, 1)
    longbow = _attack(
        "hobgoblin-longbow", "Longbow", WeaponAttackKind.RANGED, 3, 1, 8, 1,
        normal=150, long=600, poison_dice=(3, 4),
    )
    return _monster(
        id="srd-hobgoblin-warrior", name="Hobgoblin Warrior", archetype="Hobgoblin Warrior",
        challenge_rating="1/2", size="medium", armor_class=18, max_hp=11,
        speed_ft=30, initiative_bonus=3, weapon_attack=longsword,
        alternate_weapon_attacks=[longbow], combat_traits=[CombatTrait.PACK_TACTICS],
        visual=build_monster_visual("half-plate", "longsword", "humanoid"),
        source="SRD 5.2.1 p. 298 Hobgoblin Warrior",
    )
