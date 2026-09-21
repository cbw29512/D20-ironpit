from __future__ import annotations

from app.domain.models import WeaponAttack


def mean_dice(count: int, size: int) -> float:
    return count * (size + 1) / 2


def weapon_attack_value(attack: WeaponAttack) -> tuple[float, int, str]:
    """Source-visible offensive value; no target AC/save metagaming."""
    if attack.fixed_damage is not None:
        damage = float(attack.fixed_damage)
    else:
        damage = mean_dice(attack.weapon.dice_count, attack.weapon.dice_size) + attack.damage_bonus
    damage += sum(
        mean_dice(item.dice_count, item.dice_size) + item.damage_bonus
        for item in attack.on_hit_damage
    )
    if attack.on_hit_save_damage is not None:
        rider = attack.on_hit_save_damage
        full = mean_dice(rider.dice_count, rider.dice_size) + rider.damage_bonus
        damage += full * (0.75 if rider.success_damage == "half" else 0.5)
    return damage, attack.attack_bonus, attack.id
