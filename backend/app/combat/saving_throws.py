from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.grapple import apply_grapple
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.models import (
    BattleEvent,
    DamageRollComponent,
    DamageType,
    DiceRoll,
    EncounterCombatant,
    SavingThrowAction,
)
from app.domain.size import size_at_most


def legal_save_action(
    action: SavingThrowAction,
    target: EncounterCombatant,
    distance_ft: int,
) -> bool:
    if distance_ft > action.range_ft:
        return False
    return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)


def _damage_components(
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
) -> list[DamageRollComponent]:
    if action.damage_dice_count == 0 or (succeeded and action.success_damage == "none"):
        return []
    if action.damage_type is None:
        raise ValueError(f"{action.name} has damage dice but no damage type.")
    rolls = [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)]
    total = sum(rolls) + action.damage_bonus
    if succeeded and action.success_damage == "half":
        total //= 2
    return [DamageRollComponent(
        source=action.name,
        notation=f"{action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus}",
        rolls=rolls,
        modifier=action.damage_bonus,
        damage_type=DamageType(action.damage_type),
        total=max(0, total),
    )]


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
) -> BattleEvent:
    if spend_action and not is_available(actor.state, "action"):
        raise ValueError("Action is not available for a saving throw action.")
    if not legal_save_action(action, target, distance_ft):
        raise ValueError(f"{action.name} has no legal target at {distance_ft} feet.")

    save_roll, succeeded = resolve_saving_throw(target.state, action.save_ability, action.dc, dice)
    if spend_action:
        spend(actor.state, "action")
    hp_before = target.state.current_hp
    rolled_components = _damage_components(action, dice, succeeded)
    applied_total, damage_components = apply_damage_defenses(target.state, rolled_components)
    damage_roll = None
    if rolled_components:
        damage_roll = DiceRoll(
            notation=" + ".join(component.notation for component in rolled_components),
            rolls=[roll for component in rolled_components for roll in component.rolls],
            modifier=sum(component.modifier for component in rolled_components),
            total=applied_total,
        )
    if applied_total:
        apply_damage(target.state, applied_total)
        end_rage_if_incapacitated(target.state)

    applied_conditions: list[str] = []
    if not succeeded and target.state.is_alive and not target.state.is_dead and action.grapple_escape_dc is not None:
        applied_conditions = apply_grapple(
            target.state,
            actor.combatant_id,
            action.grapple_escape_dc,
            action.range_ft,
            restrains=action.restrains_while_grappled,
        )

    outcome = "SUCCEEDS" if succeeded else "FAILS"
    description = (
        f"{target.state.template.name} {outcome} a DC {action.dc} "
        f"{action.save_ability.title()} save against {actor.state.template.name}'s {action.name}."
    )
    if "grappled" in applied_conditions:
        description += f" {target.state.template.name} is Grappled."
    if "restrained" in applied_conditions:
        description += f" {target.state.template.name} is Restrained while Grappled."
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=actor.combatant_id,
        actor_name=actor.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        saving_throw_roll=save_roll,
        save_ability=action.save_ability,
        save_dc=action.dc,
        save_succeeded=succeeded,
        damage_roll=damage_roll,
        damage_components=damage_components,
        applied_condition_ids=applied_conditions,
        hp_before=hp_before,
        hp_after=target.state.current_hp,
        death_save_successes=target.state.death_save_successes,
        death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable,
        is_dead=target.state.is_dead,
        feature_id=action.id,
        animation=action.animation,
        description=description,
    )
