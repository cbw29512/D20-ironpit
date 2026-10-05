from __future__ import annotations

from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.source_effect_immunity import (
    grant_source_effect_immunity,
    has_source_effect_immunity,
)
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent


def resolve_hostile_condition_aura(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    action,
    distance: int,
    affected_states,
    dice,
) -> tuple[BattleEvent | None, int]:
    aura = action.hostile_start_turn_condition_aura
    if aura is None or aura.trigger != "enemy_turn_start" or distance > aura.radius_ft:
        return None, sequence

    if has_source_effect_immunity(target.state, action.id, source.combatant_id):
        return None, sequence

    roll, succeeded = resolve_saving_throw(
        target.state, aura.save_ability, aura.save_dc, dice, round_number=round_number,
    )
    applied: list[str] = []
    if succeeded:
        if aura.success_immunity:
            grant_source_effect_immunity(
                target.state, action.id, source.combatant_id, round_number,
                source_template=source.state.template,
                source_is_magical=aura.source_is_magical,
            )
    else:
        condition = apply_timed_condition(
            target.state, aura.condition_id, source.combatant_id,
            source_effect_id=action.id,
            source_template=source.state.template,
            source_is_magical=aura.source_is_magical,
            applied_round=round_number,
            expires_round=round_number + action.duration_rounds,
            expiry_timing=action.expiry_timing,
            expires_at_start_of_source_turn=action.expiry_timing == "source_turn_start",
            ends_if_source_incapacitated=action.ends_if_source_incapacitated,
            ends_if_source_dead=action.ends_if_source_dead,
            affected_states=affected_states,
            use_default_poison_recovery=False,
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
        ),
    ), sequence + 1
