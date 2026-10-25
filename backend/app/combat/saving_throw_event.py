from __future__ import annotations

import logging

from app.combat.saving_throw_attempt import SaveAttemptResult
from app.combat.saving_throw_damage import SaveDamageResult
from app.combat.saving_throw_effects import SaveEffectResult
from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def build_save_event(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    attempt: SaveAttemptResult,
    damage: SaveDamageResult,
    effects: SaveEffectResult,
    *,
    resource_remaining: int | None,
    hp_before: int,
    temporary_hp_before: int,
    death_success_before: int,
    death_failure_before: int,
    concentration_before: str | None,
    save_disadvantage_sources: tuple[str, ...] = (),
) -> BattleEvent:
    try:
        outcome = "SUCCEEDS" if attempt.succeeded else "FAILS"
        if attempt.automatic_failure:
            description = (
                f"{target.state.template.name} automatically FAILS a DC {action.dc} "
                f"{attempt.selected_ability.title()} save against "
                f"{actor.state.template.name}'s {action.name} because its creature "
                f"type is {target.state.template.creature_type}."
            )
        else:
            description = (
                f"{target.state.template.name} {outcome} a DC {action.dc} "
                f"{action.save_ability.title()} save against "
                f"{actor.state.template.name}'s {action.name}."
            )
            if (
                attempt.save_roll is not None
                and attempt.save_roll.outcome_override_name
            ):
                description += (
                    f" {attempt.save_roll.outcome_override_name} turns the failure "
                    f"into a success "
                    f"({attempt.save_roll.outcome_override_uses_remaining} uses remain)."
                )
        if attempt.advantage_sources:
            description += (
                f" {' and '.join(attempt.advantage_sources)} grants Advantage on the save."
            )
        if save_disadvantage_sources:
            description += (
                f" {' and '.join(save_disadvantage_sources)} imposes Disadvantage on the save."
            )
        if (
            target.state.template.progression_features.evasion
            and attempt.selected_ability == "dexterity"
            and action.success_damage == "half"
        ):
            description += " Evasion reduces the damage."
        if damage.damage_outcome == "undead_fortitude":
            description += (
                f" {target.state.template.name} succeeds on Undead Fortitude "
                "and remains at 1 HP."
            )
        if "grappled" in effects.applied_conditions:
            description += f" {target.state.template.name} is Grappled."
        if "restrained" in effects.applied_conditions:
            description += (
                f" {target.state.template.name} is Restrained while Grappled."
            )
        if effects.pushed_ft:
            description += (
                f" {target.state.template.name} is pushed {effects.pushed_ft} feet away."
            )
        if not attempt.succeeded and action.failure_sets_zero_hp:
            description += (
                f" {target.state.template.name} drops directly to 0 HP (not damage)."
            )
        description += consume_survival_save_log(target.state)
        description += consume_zero_hp_replacement_log(target.state)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="saving_throw",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=attempt.save_roll,
            save_ability=attempt.selected_ability,
            save_dc=action.dc,
            save_succeeded=attempt.succeeded,
            damage_roll=damage.damage_roll,
            damage_components=damage.damage_components,
            applied_condition_ids=effects.applied_conditions,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            temporary_hp_before=temporary_hp_before,
            temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before,
            death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable,
            is_dead=target.state.is_dead,
            feature_id=action.id,
            resource_remaining=resource_remaining,
            concentration_ended_effect_id=(
                concentration_before
                if concentration_before and target.state.concentration is None
                else None
            ),
            animation=action.animation,
            description=description,
        )
    except Exception:
        logger.exception(
            "Failed to build save event for %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
