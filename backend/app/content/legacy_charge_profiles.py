from __future__ import annotations

from app.domain.charge import ChargeDamage, ChargeProfile
from app.domain.models import CombatantTemplate, DamageType
from app.domain.size import CreatureSize


def _damage(count: int, size: int, damage_type: DamageType, bonus: int = 0) -> ChargeDamage:
    return ChargeDamage(
        dice_count=count,
        dice_size=size,
        damage_type=damage_type.value,
        damage_bonus=bonus,
    )


def _prone(
    minimum: int,
    maximum: CreatureSize,
    *,
    bonus: ChargeDamage | None = None,
    follow_up: str | None = None,
) -> ChargeProfile:
    return ChargeProfile(
        minimum_move_ft=minimum,
        max_target_size=maximum,
        prone_max_target_size=maximum,
        bonus_damage=bonus,
        follow_up_attack_id=follow_up,
    )


_PROFILES = {
    "allosaurus-claws": _prone(30, CreatureSize.LARGE, follow_up="allosaurus-bite"),
    "boar-gore": _prone(20, CreatureSize.MEDIUM, bonus=_damage(1, 6, DamageType.PIERCING)),
    "elk-ram": _prone(20, CreatureSize.LARGE, bonus=_damage(1, 6, DamageType.BLUDGEONING)),
    "giant-boar-gore": _prone(20, CreatureSize.LARGE, bonus=_damage(2, 6, DamageType.PIERCING)),
    "giant-elk-ram": _prone(20, CreatureSize.HUGE, bonus=_damage(2, 4, DamageType.BLUDGEONING)),
    "giant-goat-ram": _prone(20, CreatureSize.LARGE, bonus=_damage(2, 4, DamageType.BLUDGEONING)),
    "goat-ram": ChargeProfile(
        minimum_move_ft=20,
        replacement_damage=_damage(1, 4, DamageType.BLUDGEONING),
    ),
    "minotaur-skeleton-gore": _prone(20, CreatureSize.LARGE, bonus=_damage(2, 8, DamageType.PIERCING)),
    "rhinoceros-gore": _prone(20, CreatureSize.LARGE, bonus=_damage(2, 8, DamageType.PIERCING)),
    "triceratops-gore": _prone(20, CreatureSize.HUGE, bonus=_damage(2, 8, DamageType.PIERCING)),
    "warhorse-hooves": _prone(20, CreatureSize.LARGE, bonus=_damage(2, 4, DamageType.BLUDGEONING)),
    "warhorse-skeleton-hooves": _prone(20, CreatureSize.LARGE),
}


def apply_legacy_charge_profiles(monsters: list[CombatantTemplate]) -> list[CombatantTemplate]:
    """Migration-only adapter: lift legacy charge IDs into attack-local declarative data."""
    migrated: list[CombatantTemplate] = []
    for monster in monsters:
        attacks = [monster.weapon_attack, *monster.alternate_weapon_attacks]
        migrated_attacks = [
            attack.model_copy(update={"charge_profile": _PROFILES.get(attack.id)})
            for attack in attacks
        ]
        migrated.append(monster.model_copy(update={
            "weapon_attack": migrated_attacks[0],
            "alternate_weapon_attacks": migrated_attacks[1:],
        }))
    return migrated
