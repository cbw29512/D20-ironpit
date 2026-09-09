from __future__ import annotations

from app.combat.condition_application import apply_condition_effect
from app.combat.grapple import apply_grapple
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
        condition = apply_condition_effect(
            target,
            source_id,
            source_effect_id,
            effect,
            round_number=round_number,
            affected_states=affected_states,
        )
        if condition is not None:
            applied.append(condition)
    return list(dict.fromkeys(applied))
