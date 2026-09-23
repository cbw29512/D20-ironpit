from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll
from app.domain.progression import DeferredSaveEffect


def resolve_deferred_effect_outcome(
    target: CombatantState,
    rule: DeferredSaveEffect,
    succeeded: bool,
    dice,
    affected_states: list[CombatantState],
) -> tuple[DiceRoll | None, list[DamageRollComponent]]:
    """Apply the configured successful-save damage or failed-save zero-HP outcome."""
    damage_roll = None
    components: list[DamageRollComponent] = []

    if succeeded and rule.success_damage_dice_count:
        if rule.success_damage_type is None:
            raise ValueError(
                f"Deferred effect {rule.source_id} has damage dice without a damage type."
            )
        rolls = [
            dice.roll(rule.success_damage_dice_size)
            for _ in range(rule.success_damage_dice_count)
        ]
        raw_total = sum(rolls)
        damage_type = DamageType(rule.success_damage_type)
        raw = DamageRollComponent(
            source=rule.source_name,
            notation=f"{rule.success_damage_dice_count}d{rule.success_damage_dice_size}",
            rolls=rolls,
            modifier=0,
            damage_type=damage_type,
            total=raw_total,
        )
        applied, components = apply_damage_defenses(target, [raw])
        apply_damage(
            target,
            applied,
            damage_types={damage_type},
            dice=dice,
            affected_states=affected_states,
        )
        damage_roll = DiceRoll(
            notation=raw.notation,
            rolls=rolls,
            modifier=0,
            total=applied,
        )
    elif not succeeded and rule.failure_sets_zero_hp:
        reduce_to_zero_hit_points(
            target,
            dice=dice,
            affected_states=affected_states,
        )

    return damage_roll, components
