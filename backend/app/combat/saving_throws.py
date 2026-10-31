from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import can_see
from app.combat.dice import DiceProvider
from app.combat.opening_burst import opening_burst_available
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throw_attempt import resolve_save_attempt
from app.combat.saving_throw_damage import resolve_save_damage
from app.combat.saving_throw_effects import apply_save_effects
from app.combat.saving_throw_event import build_save_event
from app.combat.saving_throw_legality import legal_save_action
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)

__all__ = ["legal_save_action", "resolve_save_action", "resolve_saving_throw"]


def resolve_save_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    distance_ft: int,
    dice: DiceProvider,
    *,
    spend_action: bool = True,
    check_resource: bool = True,
    spend_resource: bool = True,
    shared_damage_rolls: list[int] | list[list[int]] | None = None,
    affected_states: list[CombatantState] | None = None,
    spell_effect: bool = False,
    save_disadvantage_sources: tuple[str, ...] = (),
    save_advantage_sources: tuple[str, ...] = (),
    resource_remaining_override: int | None = None,
    setup: EncounterSetup | None = None,
) -> BattleEvent:
    try:
        if (
            action.opening_initiative_only
            and not opening_burst_available(round_number, actor, setup)
        ):
            raise ValueError(
                f"{action.name} requires an initiative-winning opening turn."
            )
        if spend_action and not is_available(actor.state, action.action_cost):
            raise ValueError(
                f"{action.action_cost} is not available for {action.name}."
            )
        if not legal_save_action(
            action,
            target,
            distance_ft,
            source_id=actor.combatant_id,
            actor=actor,
        ):
            raise ValueError(
                f"{action.name} has no legal target at {distance_ft} feet."
            )
        if action.requires_target_sight and not can_see(
            actor.state, target.state
        ):
            raise ValueError(f"{action.name} requires the actor to see the target.")
        if check_resource and not action_resource_available(actor.state, action):
            raise ValueError(f"{action.name} resource is unavailable.")

        remaining = (
            spend_action_resource(actor.state, action)
            if spend_resource
            else None
        )
        if resource_remaining_override is not None:
            remaining = resource_remaining_override

        attempt = resolve_save_attempt(
            actor,
            target,
            action,
            dice,
            round_number,
            spell_effect=spell_effect,
            save_disadvantage_sources=save_disadvantage_sources,
            save_advantage_sources=save_advantage_sources,
            setup=setup,
        )
        if spend_action:
            spend(actor.state, action.action_cost)
        from app.combat.owner_action_expiry import expire_on_owner_event
        expire_on_owner_event(actor.state, "action", affected_states, action_id=action.id)

        hp_before = target.state.current_hp
        temporary_hp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes
        death_failure_before = target.state.death_save_failures
        concentration_before = (
            target.state.concentration.effect_id
            if target.state.concentration
            else None
        )

        damage = resolve_save_damage(
            target,
            attempt.action,
            dice,
            attempt.succeeded,
            shared_damage_rolls=shared_damage_rolls,
            affected_states=affected_states,
            setup=setup,
            source_id=actor.combatant_id,
        )
        effects = apply_save_effects(
            actor,
            target,
            action,
            attempt.succeeded,
            attempt.save_roll,
            round_number,
            affected_states=affected_states,
            setup=setup,
        )
        return build_save_event(
            sequence,
            round_number,
            actor,
            target,
            action,
            attempt,
            damage,
            effects,
            resource_remaining=remaining,
            hp_before=hp_before,
            temporary_hp_before=temporary_hp_before,
            death_success_before=death_success_before,
            death_failure_before=death_failure_before,
            concentration_before=concentration_before,
            save_disadvantage_sources=save_disadvantage_sources,
        )
    except Exception:
        logger.exception(
            "Failed to resolve save action %s from %s against %s.",
            action.id,
            actor.combatant_id,
            target.combatant_id,
        )
        raise
