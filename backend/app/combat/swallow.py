from __future__ import annotations

from app.combat.conditions import PRONE_EFFECT_ID
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.grapple import release_grapple
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DiceRoll, WeaponAttack
from app.domain.size import size_at_most
from app.domain.swallow import SwallowedState


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _attack(actor: EncounterCombatant, attack_id: str) -> WeaponAttack:
    attacks = [actor.state.template.weapon_attack, *actor.state.template.alternate_weapon_attacks]
    return next(item for item in attacks if item.id == attack_id)


def swallowed_targets(actor: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return [
        member for member in _members(setup)
        if member.state.swallowed is not None and member.state.swallowed.source_id == actor.combatant_id
    ]


def swallow_target(actor: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    action = actor.state.template.swallow_action
    if action is None or len(swallowed_targets(actor, setup)) >= action.max_swallowed:
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
    action = actor.state.template.swallow_action
    target = swallow_target(actor, setup)
    if action is None or target is None:
        return [], sequence, False
    attack = _attack(actor, action.attack_id)
    event = resolve_encounter_attack(sequence, round_number, actor, target, attack, 5, dice, setup)
    if event.hit and target.state.current_hp > 0 and not target.state.is_dead:
        release_grapple(target.state, actor.combatant_id)
        target.state.swallowed = SwallowedState(
            source_id=actor.combatant_id, source_effect_id=action.id,
            damage_dice_count=action.damage_dice_count, damage_dice_size=action.damage_dice_size,
            damage_bonus=action.damage_bonus, damage_type=action.damage_type,
            exit_movement_ft=action.exit_movement_ft, exit_prone=action.exit_prone,
        )
        event.applied_condition_ids = list(dict.fromkeys([*event.applied_condition_ids, "blinded", "restrained", "swallowed"]))
        event.feature_id = action.id
        event.description += f" {target.state.template.name} is swallowed."
    return [event], sequence + 1, True


def cleanup_swallowed(setup: EncounterSetup) -> None:
    members = {member.combatant_id: member for member in _members(setup)}
    for target in members.values():
        swallowed = target.state.swallowed
        if swallowed is None:
            continue
        source = members.get(swallowed.source_id)
        if source is not None and source.state.is_alive and not source.state.is_dead:
            continue
        target.state.swallowed = None
        if swallowed.exit_prone and PRONE_EFFECT_ID not in target.state.active_effect_ids:
            target.state.active_effect_ids.append(PRONE_EFFECT_ID)


def resolve_start_turn_damage(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for target in swallowed_targets(actor, setup):
        swallowed = target.state.swallowed
        if swallowed is None:
            continue
        rolls = [dice.roll(swallowed.damage_dice_size) for _ in range(swallowed.damage_dice_count)]
        rolled = DamageRollComponent(
            source="Swallow", notation=f"{swallowed.damage_dice_count}d{swallowed.damage_dice_size}+{swallowed.damage_bonus}",
            rolls=rolls, modifier=swallowed.damage_bonus, damage_type=swallowed.damage_type,
            total=sum(rolls) + swallowed.damage_bonus,
        )
        applied, components = apply_damage_defenses(target.state, [rolled])
        hp_before = target.state.current_hp
        if applied:
            apply_damage(target.state, applied, damage_types={swallowed.damage_type}, dice=dice,
                         affected_states=[member.state for member in _members(setup)])
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id="swallow", damage_roll=DiceRoll(
                notation=rolled.notation, rolls=rolls, modifier=swallowed.damage_bonus, total=applied,
            ), damage_components=components, hp_before=hp_before, hp_after=target.state.current_hp,
            animation="damage", description=f"{target.state.template.name} takes {applied} {swallowed.damage_type.value} damage while swallowed.",
        ))
        sequence += 1
    return events, sequence
