from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.aura_activation import aura_is_active
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.source_effect_immunity import grant_source_effect_immunity, source_effect_is_immune
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _sources(target: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return [member for member in [*setup.heroes, *setup.monsters] if member.combatant_id != target.combatant_id]


def resolve_start_turn_auras(
    sequence: int, round_number: int, target: EncounterCombatant, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        for source in _sources(target, setup):
            if source.state.is_dead or source.state.current_hp <= 0:
                continue
            for aura in source.state.template.start_turn_auras:
                if not aura_is_active(source.state, aura):
                    continue
                if combatant_distance(target, source) > aura.range_ft:
                    continue
                if aura.reaction_cost:
                    if source.side == target.side or not is_available(source.state, "reaction"):
                        continue
                    spend(source.state, "reaction")
                if source_effect_is_immune(target.state, source.combatant_id, aura.id):
                    continue
                roll, succeeded = resolve_saving_throw(
                    target.state, aura.save_ability, aura.save_dc, dice,
                    magical_effect=aura.magical_effect, against_condition=aura.failure_condition_id,
                )
                applied = None
                if succeeded and aura.success_grants_source_immunity:
                    grant_source_effect_immunity(target.state, source.combatant_id, aura.id)
                elif not succeeded:
                    applied = apply_timed_condition(
                        target.state, aura.failure_condition_id, source.combatant_id,
                        source_effect_id=aura.id, applied_round=round_number,
                        expires_round=round_number + aura.failure_duration_rounds,
                        expires_at_start_of_source_turn=False, expiry_timing=aura.failure_expiry_timing,
                        affected_states=affected_states,
                        blocks_reactions=aura.failure_blocks_reactions,
                        action_bonus_exclusive=aura.failure_action_bonus_exclusive,
                    )
                outcome = "SUCCEEDS" if succeeded else "FAILS"
                description = (
                    f"{target.state.template.name} {outcome} a DC {aura.save_dc} "
                    f"{aura.save_ability.title()} save against {source.state.template.name}'s {aura.name}."
                )
                if aura.reaction_cost:
                    description += f" {source.state.template.name} spends its reaction."
                if applied:
                    description += f" {target.state.template.name} is {applied.title()}."
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="saving_throw",
                    actor_id=source.combatant_id, actor_name=source.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    saving_throw_roll=roll, save_ability=aura.save_ability, save_dc=aura.save_dc,
                    save_succeeded=succeeded, applied_condition_ids=[applied] if applied else [],
                    feature_id=aura.id, animation="condition-save", description=description,
                ))
                sequence += 1
        return events, sequence
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Start-turn aura resolution failed for %s.", target.combatant_id)
        raise RuntimeError("Start-turn aura resolution failed.") from exc
