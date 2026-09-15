from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.swallow_application import apply_swallowed
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DiceRoll, WeaponAttack
from app.domain.size import size_at_most
from app.domain.swallow import SwallowAction


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _swallow_action(actor: EncounterCombatant) -> SwallowAction | None:
    return next(
        (
            action for action in actor.state.template.swallow_actions
            if action.requires_existing_grapple and action.attack_id is not None
        ),
        None,
    )


def _attack(actor: EncounterCombatant, attack_id: str) -> WeaponAttack:
    attacks = [actor.state.template.weapon_attack, *actor.state.template.alternate_weapon_attacks]
    return next(item for item in attacks if item.id == attack_id)


def swallowed_targets(actor: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return [
        member for member in _members(setup)
        if member.state.swallowed is not None and member.state.swallowed.source_id == actor.combatant_id
    ]


def swallow_target(actor: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    action = _swallow_action(actor)
    if action is None:
        return None
    swallowed_count = len(swallowed_targets(actor, setup))
    if action.max_swallowed is not None and swallowed_count >= action.max_swallowed:
        return None
    opponents = setup.monsters if actor.side == "heroes" else setup.heroes
    for target in opponents:
        held = any(source.source_id == actor.combatant_id for source in target.state.grapple_sources)
        if held and target.state.current_hp > 0 and not target.state.is_dead and size_at_most(target.state.template.size, action.max_target_size):
            return target
    return None


def resolve_swallow_action(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int, bool]:
    action = _swallow_action(actor)
    target = swallow_target(actor, setup)
    if action is None or action.attack_id is None or target is None:
        return [], sequence, False
    attack = _attack(actor, action.attack_id)
    event = resolve_encounter_attack(sequence, round_number, actor, target, attack, 5, dice, setup)
    if event.hit and target.state.current_hp > 0 and not target.state.is_dead:
        apply_swallowed(actor, target, action, event)
    return [event], sequence + 1, True


def cleanup_swallowed(setup: EncounterSetup) -> None:
    members = {member.combatant_id: member for member in _members(setup)}
    for target in members.values():
        swallowed = target.state.swallowed
        if swallowed is None or swallowed.source_dead:
            continue
        source = members.get(swallowed.source_id)
        if source is not None and source.state.is_alive and not source.state.is_dead:
            continue
        if swallowed.source_death_release == "immediate":
            target.state.swallowed = None
        else:
            swallowed.source_dead = True


def _save_result(target: EncounterCombatant, swallowed, dice: DiceProvider):
    if swallowed.start_turn_save_ability is None:
        return None, None
    if swallowed.start_turn_save_dc is None:
        raise ValueError("Containment start-turn save is missing its DC.")
    return resolve_saving_throw(
        target.state, swallowed.start_turn_save_ability, swallowed.start_turn_save_dc, dice,
    )


def resolve_start_turn_damage(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for target in swallowed_targets(actor, setup):
        swallowed = target.state.swallowed
        if swallowed is None or swallowed.source_dead:
            continue
        save_roll, save_succeeded = _save_result(target, swallowed, dice)
        hp_before = target.state.current_hp
        rolls: list[int] = []; components: list[DamageRollComponent] = []; applied = 0
        notation = f"{swallowed.damage_dice_count}d{swallowed.damage_dice_size}+{swallowed.damage_bonus}"
        if save_succeeded is not True:
            rolls = [dice.roll(swallowed.damage_dice_size) for _ in range(swallowed.damage_dice_count)]
            rolled = DamageRollComponent(
                source=swallowed.source_effect_id, notation=notation, rolls=rolls,
                modifier=swallowed.damage_bonus, damage_type=swallowed.damage_type,
                total=sum(rolls) + swallowed.damage_bonus,
            )
            applied, components = apply_damage_defenses(target.state, [rolled])
            if applied:
                apply_damage(
                    target.state, applied, damage_types={swallowed.damage_type}, dice=dice,
                    affected_states=[member.state for member in _members(setup)],
                )
        description = (
            f"{target.state.template.name} succeeds on the containment save and takes no damage."
            if save_succeeded is True else
            f"{target.state.template.name} takes {applied} {swallowed.damage_type.value} damage while contained."
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=swallowed.source_effect_id, saving_throw_roll=save_roll,
            save_ability=swallowed.start_turn_save_ability, save_dc=swallowed.start_turn_save_dc,
            save_succeeded=save_succeeded,
            damage_roll=DiceRoll(notation=notation, rolls=rolls, modifier=swallowed.damage_bonus, total=applied) if rolls else None,
            damage_components=components, hp_before=hp_before, hp_after=target.state.current_hp,
            animation="damage" if applied else "save", description=description,
        ))
        sequence += 1
    return events, sequence
