from __future__ import annotations

from app.combat.ally_roll_auras import ally_roll_aura_advantage_sources
from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _sources(target: EncounterCombatant, setup: EncounterSetup):
    return [member for member in [*setup.heroes, *setup.monsters] if member.combatant_id != target.combatant_id]


def _eligible(source: EncounterCombatant, target: EncounterCombatant, aura) -> bool:
    if source.state.is_dead or not source.state.is_alive or source.state.current_hp <= 0:
        return False
    if aura.suppressed_if_incapacitated and is_incapacitated(source.state):
        return False
    if aura.target_mode == "enemies" and source.side == target.side:
        return False
    return combatant_distance(source, target) <= aura.radius_ft


def resolve_start_turn_save_auras(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-centered saves after old target-start effects have expired."""
    events: list[BattleEvent] = []
    affected = [member.state for member in [*setup.heroes, *setup.monsters]]
    for source in _sources(target, setup):
        for aura in source.state.template.start_turn_save_auras:
            if not _eligible(source, target, aura):
                continue
            advantage = ally_roll_aura_advantage_sources(target, setup, roll_kind="saving_throw")
            roll, succeeded = resolve_saving_throw(
                target.state, aura.save_ability, aura.dc, dice, advantage_sources=advantage,
            )
            applied: list[str] = []
            if not succeeded:
                condition = apply_timed_condition(
                    target.state, aura.failure_condition, source.combatant_id,
                    source_effect_id=aura.id, applied_round=round_number,
                    expires_at_start_of_source_turn=False,
                    expiry_timing=aura.condition_expiry_timing,
                    affected_states=affected, default_poison_recovery=False,
                )
                if condition is not None:
                    applied.append(condition)
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="saving_throw",
                actor_id=source.combatant_id, actor_name=source.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                saving_throw_roll=roll, save_ability=aura.save_ability, save_dc=aura.dc,
                save_succeeded=succeeded, applied_condition_ids=applied, feature_id=aura.id,
                animation="condition-save",
                description=(
                    f"{target.state.template.name} {'SUCCEEDS' if succeeded else 'FAILS'} a DC {aura.dc} "
                    f"{aura.save_ability.title()} save against {source.state.template.name}'s {aura.name}."
                ),
            ))
            sequence += 1
    return events, sequence
