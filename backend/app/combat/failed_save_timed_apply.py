from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def apply_failed_save_timed_effect(
    target: EncounterCombatant,
    actor: EncounterCombatant,
    action: SavingThrowAction,
    round_number: int,
    affected_states: list[CombatantState] | None,
    setup: EncounterSetup | None = None,
) -> str | list[str] | None:
    """Apply one condition compatibly, or a grouped set through one lifecycle owner."""
    try:
        rider = action.failed_save_timed_effect
        if rider is None:
            return None
        applied: list[str] = []
        condition_ids = [rider.effect_id, *rider.additional_effect_ids]
        for index, effect_id in enumerate(condition_ids):
            # A secondary condition is meaningful only when the primary effect
            # applies. It shares the source-effect group but owns no timers or
            # repeat saves, preventing duplicate lifecycle rolls.
            if index and not applied:
                break
            owns_lifecycle = index == 0
            ground_contact = rider.ground_contact if owns_lifecycle else False
            result = apply_timed_condition(
                target.state,
                effect_id,
                actor.combatant_id,
                source_effect_id=action.id,
                source_template=actor.state.template,
                target_actor=target,
                setup=setup,
                source_is_magical=action.magical_effect,
                applied_round=round_number,
                expires_round=(
                    round_number + rider.duration_rounds
                    if owns_lifecycle and rider.duration_rounds is not None
                    else None
                ),
                expires_at_start_of_source_turn=False,
                expiry_timing=rider.expiry_timing if owns_lifecycle else None,
                repeat_save_ability=rider.repeat_save_ability if owns_lifecycle else None,
                repeat_save_dc=rider.repeat_save_dc if owns_lifecycle else None,
                repeat_save_timing=rider.repeat_save_timing if owns_lifecycle else None,
                damage_repeat_save_trigger=(
                    rider.damage_repeat_save_trigger if owns_lifecycle else "none"
                ),
                repeat_save_disadvantage_while_source_visible=(
                    rider.repeat_save_disadvantage_while_source_visible
                    if owns_lifecycle else False
                ),
                repeat_save_failure_condition_id=(
                    rider.repeat_save_failure_condition_id if owns_lifecycle else None
                ),
                allowed_removal_action_ids=(
                    list(rider.allowed_removal_action_ids) if owns_lifecycle else []
                ),
                turn_behavior=rider.turn_behavior if owns_lifecycle else "normal",
                ends_on_damage=rider.ends_on_damage if owns_lifecycle else False,
                ends_if_source_incapacitated=(
                    rider.ends_if_source_incapacitated if owns_lifecycle else False
                ),
                ends_if_source_dead=rider.ends_if_source_dead if owns_lifecycle else False,
                next_attack_disadvantage=(
                    rider.next_attack_disadvantage if owns_lifecycle else False
                ),
                suppress_reactions=rider.blocks_reactions if owns_lifecycle else False,
                control_limits=rider.compiled_limits() if owns_lifecycle else None,
                affected_states=affected_states,
                use_default_poison_recovery=False,
                repeat_save_failures_to_lock=(
                    rider.repeat_save_failures_to_lock if owns_lifecycle else None
                ),
                escape_check_ability=rider.escape_check_ability if owns_lifecycle else None,
                escape_check_dc=rider.escape_check_dc if owns_lifecycle else None,
                ground_contact=ground_contact,
                ends_on_teleport=(
                    (rider.ends_on_teleport or ground_contact) if owns_lifecycle else False
                ),
                source_effect_immunity_on_end=(
                    rider.source_effect_immunity_on_end if owns_lifecycle else False
                ),
            )
            if result is not None:
                applied.append(result)
        if not rider.additional_effect_ids:
            return applied[0] if applied else None
        return applied
    except Exception:
        logger.exception(
            "Failed-save timed rider could not be applied for %s.",
            action.id,
        )
        raise
