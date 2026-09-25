from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log

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
from app.domain.save_damage import SaveDamageComponent
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_most


def legal_save_action(action: SavingThrowAction, target: EncounterCombatant, distance_ft: int) -> bool:
    if distance_ft > action.range_ft: return False
    return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)


def _damage_specs(action: SavingThrowAction) -> list[SaveDamageComponent]:
    if action.damage_components:
        if action.damage_dice_count or action.damage_type is not None or action.damage_bonus:
            raise ValueError(f"{action.name} mixes component and legacy save damage.")
        return list(action.damage_components)
    if action.damage_dice_count == 0:
        return []
    if action.damage_type is None:
        raise ValueError(f"{action.name} has damage dice but no damage type.")
    return [SaveDamageComponent(
        dice_count=action.damage_dice_count,
        dice_size=action.damage_dice_size,
        damage_bonus=action.damage_bonus,
        damage_type=action.damage_type,
    )]


def _shared_component_rolls(
    specs: list[SaveDamageComponent],
    shared: list[int] | list[list[int]] | None,
) -> list[list[int] | None]:
    if shared is None:
        return [None] * len(specs)
    if len(specs) == 1 and all(isinstance(item, int) for item in shared):
        return [list(shared)]
    if len(shared) != len(specs) or not all(isinstance(item, list) for item in shared):
        raise ValueError("Shared save damage rolls do not match the component count.")
    return [list(item) for item in shared]


def _damage_rolls(spec: SaveDamageComponent, dice: DiceProvider, shared: list[int] | None) -> list[int]:
    rolls = [dice.roll(spec.dice_size) for _ in range(spec.dice_count)] if shared is None else list(shared)
    if len(rolls) != spec.dice_count or any(not 1 <= roll <= spec.dice_size for roll in rolls):
        raise ValueError("Shared save damage rolls do not match the component dice.")
    return rolls


def _damage_components(
    state: CombatantState,
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | list[list[int]] | None = None,
) -> list[DamageRollComponent]:
    specs = _damage_specs(action)
    if not specs or (succeeded and action.success_damage == "none"):
        return []
    shared = _shared_component_rolls(specs, shared_damage_rolls)
    components: list[DamageRollComponent] = []
    for spec, component_rolls in zip(specs, shared, strict=True):
        rolls = _damage_rolls(spec, dice, component_rolls)
        raw_total = sum(rolls) + spec.damage_bonus
        total = evasion_damage(state, action.save_ability, succeeded, action.success_damage, raw_total)
        components.append(DamageRollComponent(
            source=action.name,
            notation=f"{spec.dice_count}d{spec.dice_size}+{spec.damage_bonus}",
            rolls=rolls,
            modifier=spec.damage_bonus,
            damage_type=DamageType(spec.damage_type),
            total=max(0, total),
        ))
    return components

def resolve_save_action(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
    action: SavingThrowAction, distance_ft: int, dice: DiceProvider, *, spend_action: bool = True,
    check_resource: bool = True, spend_resource: bool = True,
    shared_damage_rolls: list[int] | list[list[int]] | None = None, affected_states: list[CombatantState] | None = None,
) -> BattleEvent:
    if spend_action and not is_available(actor.state, "action"): raise ValueError("Action is not available for a saving throw action.")
    if not legal_save_action(action, target, distance_ft): raise ValueError(f"{action.name} has no legal target at {distance_ft} feet.")
    if check_resource and not action_resource_available(actor.state, action):
        raise ValueError(f"{action.name} resource is unavailable.")
    remaining = spend_action_resource(actor.state, action) if spend_resource else None
    save_context = SavingThrowContext(magical_effect=action.magical_effect)
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
    rolled_components = _damage_components(target.state, action, dice, succeeded, shared_damage_rolls)
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
