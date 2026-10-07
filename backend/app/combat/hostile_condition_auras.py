from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.domain.saving_throw_context import SavingThrowContext

from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.source_effect_immunity import (
    grant_source_effect_immunity,
    has_source_effect_immunity,
)
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def resolve_hostile_condition_aura(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    action,
    distance: int,
    affected_states,
    dice,
    setup=None,
) -> tuple[BattleEvent | None, int]:
    try:
        aura = action.hostile_start_turn_condition_aura
        if aura is None or aura.trigger != "enemy_turn_start" or distance > aura.radius_ft:
            return None, sequence
        if aura.recipient_scope == "enemies" and source.side == target.side:
            return None, sequence

        if target.state.is_dead or condition_is_immune(
            target.state, aura.condition_id, source.state.template,
            source_is_magical=aura.source_is_magical,
        ):
            return None, sequence

        if has_source_effect_immunity(target.state, action.id, source.combatant_id):
            return None, sequence

        roll, succeeded = resolve_saving_throw(
            target.state, aura.save_ability, aura.save_dc, dice,
            SavingThrowContext(
                condition_id=aura.condition_id,
                magical_effect=aura.source_is_magical,
                source_creature_type=source.state.template.creature_type,
                effect_tags=frozenset([aura.condition_id, *aura.effect_tags]),
            ),
            round_number=round_number, encounter_roller=target, setup=setup,
        )
        applied: list[str] = []
        immunity_granted = False
        if succeeded:
            if aura.success_immunity:
                immunity_granted = grant_source_effect_immunity(
                    target.state, action.id, source.combatant_id, round_number,
                    source_template=source.state.template,
                    source_is_magical=aura.source_is_magical,
                ) is not None
        else:
            # The condition may end earlier than the source aura (e.g. next turn).
            duration = aura.condition_duration_rounds or action.duration_rounds
            expiry = aura.condition_expiry_timing or action.expiry_timing
            condition = apply_timed_condition(
                target.state, aura.condition_id, source.combatant_id,
                source_effect_id=action.id,
                source_template=source.state.template,
                source_is_magical=aura.source_is_magical,
                applied_round=round_number,
                expires_round=round_number + duration if duration is not None else None,
                expiry_timing=expiry,
                expires_at_start_of_source_turn=expiry == "source_turn_start",
                ends_if_source_incapacitated=action.ends_if_source_incapacitated,
                ends_if_source_dead=action.ends_if_source_dead,
                affected_states=affected_states,
                use_default_poison_recovery=False,
                suppress_reactions=aura.suppress_reactions,
                control_limits=aura.control_limits,
            )
            if condition is not None:
                applied.append(condition)

        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability=aura.save_ability,
            save_dc=aura.save_dc, save_succeeded=succeeded,
            applied_condition_ids=applied, distance_before_ft=distance,
            feature_id=action.id, animation=action.animation,
            description=(
                f"{target.state.template.name} starts its turn within {distance} feet of "
                f"{source.state.template.name}'s {action.name} and "
                f"{'resists' if succeeded else 'fails against'} its aura."
                + (f" Immune to this source's {action.name} for the rest of the match." if immunity_granted else "")
            ),
        ), sequence + 1
    except Exception:
        logger.exception(
            "Failed condition aura %s from %s against %s in round %s.",
            action.id, source.combatant_id, target.combatant_id, round_number,
        )
        raise
