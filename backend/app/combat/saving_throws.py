from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.grapple import apply_grapple
from app.combat.failed_d20_test_override import source_name_for_roll
from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
from app.combat.rogue_defenses import evasion_damage
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll, EncounterCombatant, SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_most


def legal_save_action(action: SavingThrowAction, target: EncounterCombatant, distance_ft: int) -> bool:
    if distance_ft > action.range_ft: return False
    return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)


def _damage_rolls(action: SavingThrowAction, dice: DiceProvider, shared_damage_rolls: list[int] | None) -> list[int]:
    if shared_damage_rolls is None: return [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)]
    if len(shared_damage_rolls) != action.damage_dice_count: raise ValueError(f"{action.name} shared damage roll count does not match its damage dice.")
    if any(not 1 <= roll <= action.damage_dice_size for roll in shared_damage_rolls): raise ValueError(f"{action.name} shared damage rolls contain an invalid die result.")
    return list(shared_damage_rolls)


def _component_damage_rolls(component, dice: DiceProvider, shared: list[int] | None) -> list[int]:
    try:
        if shared is None:
            return [dice.roll(component.dice_size) for _ in range(component.dice_count)]
        if len(shared) != component.dice_count:
            raise ValueError("Shared typed damage roll count does not match its damage component.")
        if any(not 1 <= roll <= component.dice_size for roll in shared):
            raise ValueError("Shared typed damage rolls contain an invalid die result.")
        return list(shared)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Typed save damage rolls could not be resolved.") from exc


def _damage_components(
    state: CombatantState,
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | None = None,
    shared_damage_component_rolls: list[list[int]] | None = None,
) -> list[DamageRollComponent]:
    try:
        if succeeded and action.success_damage == "none":
            return []
        if action.damage_components:
            if shared_damage_rolls is not None:
                raise ValueError("Legacy shared damage rolls cannot be combined with typed damage components.")
            if shared_damage_component_rolls is not None and len(shared_damage_component_rolls) != len(action.damage_components):
                raise ValueError("Shared typed damage component count does not match the action.")
            resolved: list[DamageRollComponent] = []
            for index, component in enumerate(action.damage_components):
                shared = shared_damage_component_rolls[index] if shared_damage_component_rolls is not None else None
                rolls = _component_damage_rolls(component, dice, shared)
                raw_total = sum(rolls) + component.damage_bonus
                total = evasion_damage(state, action.save_ability, succeeded, action.success_damage, raw_total)
                resolved.append(DamageRollComponent(
                    source=component.source or action.name,
                    notation=f"{component.dice_count}d{component.dice_size}+{component.damage_bonus}",
                    rolls=rolls,
                    modifier=component.damage_bonus,
                    damage_type=DamageType(component.damage_type),
                    total=max(0, total),
                ))
            return resolved
        if action.damage_dice_count == 0:
            return []
        if action.damage_type is None:
            raise ValueError(f"{action.name} has damage dice but no damage type.")
        rolls = _damage_rolls(action, dice, shared_damage_rolls)
        raw_total = sum(rolls) + action.damage_bonus
        total = evasion_damage(state, action.save_ability, succeeded, action.success_damage, raw_total)
        return [DamageRollComponent(
            source=action.name,
            notation=f"{action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus}",
            rolls=rolls,
            modifier=action.damage_bonus,
            damage_type=DamageType(action.damage_type),
            total=max(0, total),
        )]
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Saving throw damage components could not be resolved.") from exc


def resolve_save_action(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
    action: SavingThrowAction, distance_ft: int, dice: DiceProvider, *, spend_action: bool = True,
    check_resource: bool = True, spend_resource: bool = True,
    shared_damage_rolls: list[int] | None = None,
    shared_damage_component_rolls: list[list[int]] | None = None,
    affected_states: list[CombatantState] | None = None,
) -> BattleEvent:
    if spend_action and not is_available(actor.state, "action"): raise ValueError("Action is not available for a saving throw action.")
    if not legal_save_action(action, target, distance_ft): raise ValueError(f"{action.name} has no legal target at {distance_ft} feet.")
    if check_resource and not action_resource_available(actor.state, action):
        raise ValueError(f"{action.name} resource is unavailable.")
    remaining = spend_action_resource(actor.state, action) if spend_resource else None
    save_context = SavingThrowContext(
        magical_effect=action.magical_effect,
        effect_tags=frozenset(
            {action.damage_type} if action.damage_type else {
                component.damage_type for component in action.damage_components
            }
        ),
    )
    advantage_sources = saving_throw_advantage_source_names(
        target.state, action.save_ability, save_context,
    )
    save_roll, succeeded = resolve_saving_throw(
        target.state, action.save_ability, action.dc, dice, save_context,
    )
    if spend_action: spend(actor.state, "action")
    hp_before = target.state.current_hp; temporary_hp_before = target.state.temporary_hp
    death_success_before = target.state.death_save_successes; death_failure_before = target.state.death_save_failures
    concentration_before = target.state.concentration.effect_id if target.state.concentration else None
    rolled_components = _damage_components(
        target.state,
        action,
        dice,
        succeeded,
        shared_damage_rolls,
        shared_damage_component_rolls,
    )
    applied_total, damage_components = apply_damage_defenses(target.state, rolled_components)
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
        applied_conditions = apply_grapple(target.state, actor.combatant_id, action.grapple_escape_dc, action.range_ft, restrains=action.restrains_while_grappled)
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
        animation=action.animation, description=description + consume_survival_save_log(target.state),
    )
