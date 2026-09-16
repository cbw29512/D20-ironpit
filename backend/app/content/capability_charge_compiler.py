from __future__ import annotations

from app.domain.charge import AttackChargeProfile, ChargeDamage


def compile_charge(definition) -> AttackChargeProfile | None:
    if definition is None:
        return None

    def damage(value):
        if value is None:
            return None
        return ChargeDamage(
            dice_count=value.dice_count,
            dice_size=value.dice_size,
            damage_type=value.damage_type,
            damage_bonus=value.damage_bonus,
        )

    return AttackChargeProfile(
        minimum_move_ft=definition.minimum_move_ft,
        max_target_size=definition.max_target_size,
        prone_max_target_size=definition.prone_max_target_size,
        prone_save_ability=definition.prone_save_ability,
        prone_save_dc=definition.prone_save_dc,
        bonus_damage=damage(definition.bonus_damage),
        replacement_damage=damage(definition.replacement_damage),
        follow_up_attack_id=definition.follow_up_attack_id,
        follow_up_required_target_condition=definition.follow_up_required_target_condition,
        follow_up_action_cost=definition.follow_up_action_cost,
    )
