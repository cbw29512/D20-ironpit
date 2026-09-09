from __future__ import annotations

from collections.abc import Iterable

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.effect_gates import evaluate_effect_gate
from app.combat.grapple import apply_grapple
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import HitControlEffect
from app.domain.runtime import CombatantState
from app.domain.size import size_at_most


def apply_persistent_effects(
    target: CombatantState,
    effects: Iterable[HitControlEffect],
    *,
    source_id: str,
    source_effect_id: str,
    range_ft: int,
    round_number: int | None = None,
    affected_states: list[CombatantState] | None = None,
    dice: DiceProvider | None = None,
) -> list[str]:
    """Apply only effects whose universal requirements and save gates pass."""
    if target.is_dead or not target.is_alive:
        return []

    applied: list[str] = []
    for effect in effects:
        if effect.max_target_size is not None and not size_at_most(target.template.size, effect.max_target_size):
            continue
        if not evaluate_effect_gate(target, effect.gate, dice).passes:
            continue
        if effect.grapple_escape_dc is not None:
            applied.extend(apply_grapple(
                target, source_id, effect.grapple_escape_dc, range_ft,
                restrains=effect.restrains_while_grappled,
            ))
        if effect.condition_id is None or condition_is_immune(target, effect.condition_id):
            continue
        if effect.condition_id == "prone":
            if "prone" not in target.active_effect_ids:
                target.active_effect_ids.append("prone")
            applied.append("prone")
            continue
        condition = apply_timed_condition(
            target, effect.condition_id, source_id,
            source_effect_id=source_effect_id,
            applied_round=round_number,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expiry_timing=effect.expiry_timing,
            repeat_save_ability=effect.repeat_save_ability,
            repeat_save_dc=effect.repeat_save_dc,
            repeat_save_timing=effect.repeat_save_timing,
            allowed_removal_action_ids=effect.allowed_removal_action_ids,
            affected_states=affected_states,
        )
        if condition is not None:
            applied.append(condition)
    return list(dict.fromkeys(applied))
