from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.models import CombatantState
from app.domain.timed_control_limits import compiled_control_limits

logger = logging.getLogger(__name__)


def apply_damage_taken_timed_effects(
    state: CombatantState,
    damage_before: dict[str, int],
) -> list[str]:
    """Apply source-declared timed effects only when qualifying typed damage increased."""
    try:
        applied: list[str] = []
        for rule in state.template.damage_taken_timed_effects:
            damage_type = rule.trigger_damage_type.value
            before = int(damage_before.get(damage_type, 0))
            after = int(state.damage_taken_this_turn_by_type.get(damage_type, 0))
            if after <= before:
                continue
            limits = compiled_control_limits(
                attack_roll_disadvantage=rule.attack_roll_disadvantage,
                ability_check_disadvantage=rule.ability_check_disadvantage,
            )
            result = apply_timed_condition(
                state,
                rule.effect_id,
                state.template.id,
                source_effect_id=rule.source_id,
                expires_at_start_of_source_turn=False,
                expiry_timing="target_turn_end",
                expires_target_turn_count=state.turns_started + rule.target_turns,
                use_default_poison_recovery=False,
                control_limits=limits,
            )
            if result is not None:
                applied.append(result)
        return applied
    except Exception as exc:
        logger.exception("Damage-triggered timed effects failed for %s.", state.template.name)
        raise RuntimeError("Damage-triggered timed effects could not be resolved.") from exc
