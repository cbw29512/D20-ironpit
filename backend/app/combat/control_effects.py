from __future__ import annotations

from app.combat.grapple import apply_grapple
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import HitControlEffect
from app.domain.runtime import CombatantState
from app.domain.size import size_at_most


def apply_control_effect(
    target: CombatantState,
    source_id: str,
    source_effect_id: str,
    effect: HitControlEffect | None,
    *,
    range_ft: int,
    round_number: int | None = None,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    """Apply one source-neutral persistent control payload after its trigger succeeds."""
    if effect is None or target.is_dead or not target.is_alive:
        return []
    if effect.max_target_size is not None and not size_at_most(target.template.size, effect.max_target_size):
        return []

    applied: list[str] = []
    if effect.grapple_escape_dc is not None:
        applied.extend(apply_grapple(
            target,
            source_id,
            effect.grapple_escape_dc,
            range_ft,
            restrains=effect.restrains_while_grappled,
        ))
    if effect.condition_id is not None:
        timed = apply_timed_condition(
            target,
            effect.condition_id,
            source_id,
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
        if timed is not None:
            applied.append(timed)
    return list(dict.fromkeys(applied))
