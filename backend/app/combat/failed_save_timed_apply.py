from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def apply_failed_save_timed_effect(
    target: EncounterCombatant,
    actor: EncounterCombatant,
    action: SavingThrowAction,
    round_number: int,
    affected_states: list[CombatantState] | None,
) -> str | None:
    """Apply one failed-save timed rider, including ground-contact / teleport-cancel tags."""
    try:
        rider = action.failed_save_timed_effect
        if rider is None:
            return None
        ground_contact = rider.ground_contact
        ends_on_teleport = rider.ends_on_teleport or ground_contact
        return apply_timed_condition(
            target.state,
            rider.effect_id,
            actor.combatant_id,
            source_effect_id=action.id,
            source_template=actor.state.template,
            source_is_magical=action.magical_effect,
            applied_round=round_number,
            expires_round=(
                round_number + rider.duration_rounds if rider.duration_rounds is not None else None
            ),
            expiry_timing=rider.expiry_timing,
            repeat_save_ability=rider.repeat_save_ability,
            repeat_save_dc=rider.repeat_save_dc,
            repeat_save_timing=rider.repeat_save_timing,
            turn_behavior=rider.turn_behavior,
            ends_on_damage=rider.ends_on_damage,
            ends_if_source_incapacitated=rider.ends_if_source_incapacitated,
            ends_if_source_dead=rider.ends_if_source_dead,
            next_attack_disadvantage=rider.next_attack_disadvantage,
            suppress_reactions=rider.blocks_reactions,
            control_limits=rider.compiled_limits(),
            affected_states=affected_states,
            use_default_poison_recovery=False,
            repeat_save_failures_to_lock=rider.repeat_save_failures_to_lock,
            escape_check_ability=rider.escape_check_ability,
            escape_check_dc=rider.escape_check_dc,
            ground_contact=ground_contact,
            ends_on_teleport=ends_on_teleport,
            source_effect_immunity_on_end=rider.source_effect_immunity_on_end,
        )
    except Exception:
        logger.exception(
            "Failed-save timed rider could not be applied for %s.",
            action.id,
        )
        raise
