from __future__ import annotations

from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp_stabilization import stabilize_at_zero
from app.domain.models import CombatantState, DamageRollComponent
from app.domain.weapons import OnHitSaveDamage


def save_damage_caused_zero(
    hp_buffer_before: int,
    applied_total: int,
    components: list[DamageRollComponent],
    effect: OnHitSaveDamage | None,
    *,
    save_component_present: bool,
) -> bool:
    if effect is None or effect.zero_hp_rider is None or not save_component_present or not components:
        return False
    save_applied = components[-1].applied_total
    non_save_applied = applied_total - save_applied
    return save_applied > 0 and hp_buffer_before > non_save_applied and hp_buffer_before <= applied_total


def apply_zero_hp_save_damage_rider(
    defender: CombatantState,
    effect: OnHitSaveDamage,
    turn_key: str,
    affected_states: list[CombatantState] | None,
) -> None:
    rider = effect.zero_hp_rider
    if rider is None:
        return
    round_text, separator, source_id = turn_key.partition(":")
    if not separator or not source_id:
        raise ValueError("Zero-HP save-damage riders require a round:source turn key.")
    round_number = int(round_text)
    stabilize_at_zero(defender)
    source_effect_id = f"{effect.source}:zero-hp-save-damage"
    for condition_id in rider.condition_ids:
        apply_timed_condition(
            defender,
            condition_id,
            source_id,
            source_effect_id=source_effect_id,
            applied_round=round_number,
            expires_round=round_number + rider.duration_rounds,
            expires_at_start_of_source_turn=False,
            expiry_timing="target_turn_start",
            affected_states=affected_states,
            use_default_poison_recovery=False,
        )
