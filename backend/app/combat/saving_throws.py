from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.dice import DiceProvider
from app.combat.grapple import apply_grapple
from app.combat.failed_d20_test_override import source_name_for_roll
from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll, EncounterCombatant, SavingThrowAction
from app.domain.runtime import CombatantState
from app.combat.save_damage_components import resolve_save_damage_components
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_most


def legal_save_action(action: SavingThrowAction, target: EncounterCombatant, distance_ft: int) -> bool:
    if distance_ft > action.range_ft: return False
    return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)


def resolve_save_action(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
    action: SavingThrowAction, distance_ft: int, dice: DiceProvider, *, spend_action: bool = True,
    check_resource: bool = True, spend_resource: bool = True,
    shared_damage_rolls: list[int] | list[list[int]] | None = None, affected_states: list[CombatantState] | None = None,
    spell_effect: bool = False,
) -> BattleEvent:
    if spend_action and not is_available(actor.state, "action"): raise ValueError("Action is not available for a saving throw action.")
    if not legal_save_action(action, target, distance_ft): raise ValueError(f"{action.name} has no legal target at {distance_ft} feet.")
    if check_resource and not action_resource_available(actor.state, action):
        raise ValueError(f"{action.name} resource is unavailable.")
    remaining = spend_action_resource(actor.state, action) if spend_resource else None
    source_type = str(actor.state.template.creature_type).split(" (")[0].strip().casefold() if actor.state.template.creature_type else None
    effect_tags = {str(tag).strip().casefold() for tag in action.effect_tags if str(tag).strip()}
    if str(action.damage_type or "").casefold() == "poison":
        effect_tags.add("poison")
    save_context = SavingThrowContext(
        magical_effect=action.magical_effect,
        spell_effect=spell_effect,
        source_creature_type=source_type,
        effect_tags=frozenset(effect_tags),
    )
    advantage_sources = saving_throw_advantage_source_names(
        target.state, action.save_ability, save_context,
    )
    save_roll, succeeded = resolve_saving_throw(
        target.state, action.save_ability, action.dc, dice, save_context, round_number=round_number,
    )
    if spend_action: spend(actor.state, "action")
    hp_before = target.state.current_hp; temporary_hp_before = target.state.temporary_hp
    death_success_before = target.state.death_save_successes; death_failure_before = target.state.death_save_failures
    concentration_before = target.state.concentration.effect_id if target.state.concentration else None
    applied_total, rolled_components, damage_components = resolve_save_damage_components(
        target.state, action, dice, succeeded, shared_damage_rolls,
    )
    damage_roll = None; damage_outcome = None
    if rolled_components:
        damage_roll = DiceRoll(notation=" + ".join(component.notation for component in rolled_components),
                               rolls=[roll for component in rolled_components for roll in component.rolls],
                               modifier=sum(component.modifier for component in rolled_components), total=applied_total)
    if applied_total:
        applied_types = {part.damage_type for part in damage_components if part.applied_total > 0}
        damage_outcome = apply_damage(target.state, applied_total, damage_types=applied_types, dice=dice, affected_states=affected_states)
        end_rage_if_incapacitated(target.state)
    applied_conditions: list[str] = []
    if not succeeded and target.state.is_alive and not target.state.is_dead and action.grapple_escape_dc is not None:
        applied_conditions = apply_grapple(
            target.state,
            actor.combatant_id,
            action.grapple_escape_dc,
            action.range_ft,
            restrains=action.restrains_while_grappled,
            source_is_magical=action.magical_effect,
        )
    outcome = "SUCCEEDS" if succeeded else "FAILS"
    description = f"{target.state.template.name} {outcome} a DC {action.dc} {action.save_ability.title()} save against {actor.state.template.name}'s {action.name}."
    if advantage_sources:
        source_text = " and ".join(advantage_sources)
        description += f" {source_text} grants Advantage on the save."
    if target.state.template.progression_features.evasion and action.save_ability == "dexterity" and action.success_damage == "half":
        description += " Evasion reduces the damage."
    if damage_outcome == "undead_fortitude": description += f" {target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP."
    if "grappled" in applied_conditions: description += f" {target.state.template.name} is Grappled."
    if "restrained" in applied_conditions: description += f" {target.state.template.name} is Restrained while Grappled."
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="saving_throw", actor_id=actor.combatant_id, actor_name=actor.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name, saving_throw_roll=save_roll,
        save_ability=action.save_ability, save_dc=action.dc, save_succeeded=succeeded, damage_roll=damage_roll, damage_components=damage_components,
        applied_condition_ids=applied_conditions, hp_before=hp_before, hp_after=target.state.current_hp,
        temporary_hp_before=temporary_hp_before, temporary_hp_after=target.state.temporary_hp,
        death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
        death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable, is_dead=target.state.is_dead, feature_id=action.id,
        resource_remaining=remaining,
        concentration_ended_effect_id=concentration_before if concentration_before and target.state.concentration is None else None,
        animation=action.animation, description=description + consume_survival_save_log(target.state) + consume_zero_hp_replacement_log(target.state),
    )
