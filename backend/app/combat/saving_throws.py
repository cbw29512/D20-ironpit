from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.forced_movement import apply_save_failure_push
from app.combat.grapple import apply_grapple
from app.combat.resources import resource_available, spend_resource
from app.combat.save_failure_effects import apply_save_failure_effects
from app.combat.saving_throw_damage import build_save_damage_components
from app.combat.saving_throw_description import describe_save_outcome
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DiceRoll, EncounterCombatant, SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def legal_save_action(action: SavingThrowAction, target: EncounterCombatant, distance_ft: int) -> bool:
    try:
        if distance_ft > action.range_ft:
            return False
        if action.forbid_target_affected_by_action and any(
            effect.source_effect_id == action.id for effect in target.state.timed_effects
        ):
            return False
        return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)
    except Exception:
        logger.exception("Failed save-action legality check for %s.", action.id)
        raise


def resolve_save_action(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
    action: SavingThrowAction, distance_ft: int, dice: DiceProvider, *, spend_action: bool = True,
    spend_resource_cost: bool = True, shared_damage_rolls: list[int] | None = None,
    capture_shared_damage_rolls: list[int] | None = None,
    affected_states: list[CombatantState] | None = None,
) -> BattleEvent:
    try:
        if spend_action and not is_available(actor.state, "action"):
            raise ValueError("Action is not available for a saving throw action.")
        if not legal_save_action(action, target, distance_ft):
            raise ValueError(f"{action.name} has no legal target at {distance_ft} feet.")
        if spend_resource_cost and not resource_available(actor.state, action.resource_id, action.resource_cost):
            raise ValueError(f"{action.name} does not have its required resource available.")
        save_roll, succeeded = resolve_saving_throw(target.state, action.save_ability, action.dc, dice)
        if spend_action:
            spend(actor.state, "action")
        resource_remaining = (
            spend_resource(actor.state, action.resource_id, action.resource_cost)
            if spend_resource_cost else None
        )
        hp_before = target.state.current_hp
        temporary_hp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes
        death_failure_before = target.state.death_save_failures
        concentration_before = target.state.concentration.effect_id if target.state.concentration else None
        tracks_push = action.push_target_away_ft > 0
        distance_before = abs(target.position_ft - actor.position_ft) if tracks_push else None
        rolled_components = build_save_damage_components(
            action, dice, succeeded, shared_damage_rolls, capture_shared_damage_rolls,
        )
        applied_total, damage_components = apply_damage_defenses(target.state, rolled_components)
        damage_roll = None
        damage_outcome = None
        if rolled_components:
            damage_roll = DiceRoll(
                notation=" + ".join(component.notation for component in rolled_components),
                rolls=[roll for component in rolled_components for roll in component.rolls],
                modifier=sum(component.modifier for component in rolled_components),
                total=applied_total,
            )
        if applied_total:
            applied_types = {part.damage_type for part in damage_components if part.applied_total > 0}
            damage_outcome = apply_damage(
                target.state, applied_total, damage_types=applied_types, dice=dice, affected_states=affected_states,
            )
            end_rage_if_incapacitated(target.state)
        applied_conditions: list[str] = []
        movement_ft = 0
        if not succeeded and target.state.is_alive and not target.state.is_dead:
            applied_conditions.extend(apply_save_failure_effects(
                target.state,
                actor.combatant_id,
                action.id,
                action.failure_effects,
                round_number=round_number,
                range_ft=action.range_ft,
                affected_states=affected_states,
            ))
            movement_ft = apply_save_failure_push(actor, target, action, save_failed=True)
            if action.grapple_escape_dc is not None:
                applied_conditions.extend(apply_grapple(
                    target.state, actor.combatant_id, action.grapple_escape_dc, action.range_ft,
                    restrains=action.restrains_while_grappled,
                ))
        applied_conditions = list(dict.fromkeys(applied_conditions))
        distance_after = abs(target.position_ft - actor.position_ft) if tracks_push else None
        description = describe_save_outcome(
            target_name=target.state.template.name,
            actor_name=actor.state.template.name,
            action_name=action.name,
            dc=action.dc,
            save_ability=action.save_ability,
            succeeded=succeeded,
            movement_ft=movement_ft,
            damage_outcome=damage_outcome,
            applied_conditions=applied_conditions,
        )
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=save_roll, save_ability=action.save_ability, save_dc=action.dc,
            save_succeeded=succeeded, damage_roll=damage_roll, damage_components=damage_components,
            applied_condition_ids=applied_conditions, hp_before=hp_before, hp_after=target.state.current_hp,
            temporary_hp_before=temporary_hp_before, temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead, feature_id=action.id,
            resource_remaining=resource_remaining, movement_ft=movement_ft,
            distance_before_ft=distance_before, distance_after_ft=distance_after,
            concentration_ended_effect_id=(
                concentration_before if concentration_before and target.state.concentration is None else None
            ),
            animation=action.animation, description=description,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Saving-throw action failed: %s -> %s.", actor.combatant_id, target.combatant_id)
        raise RuntimeError("Saving-throw action resolution failed.") from exc
