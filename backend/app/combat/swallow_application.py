from __future__ import annotations

from app.combat.grapple import release_grapple
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.size import size_at_most
from app.domain.swallow import SwallowAction, SwallowedState


def _action_for_attack(attacker: EncounterCombatant, attack: WeaponAttack) -> SwallowAction | None:
    return next(
        (
            action for action in attacker.state.template.swallow_actions
            if action.attack_id == attack.id and action.on_hit_save_ability is not None
        ),
        None,
    )


def _capacity_available(attacker: EncounterCombatant, setup: EncounterSetup, action: SwallowAction) -> bool:
    if action.max_swallowed is None:
        return True
    swallowed = sum(
        int(member.state.swallowed is not None and member.state.swallowed.source_id == attacker.combatant_id)
        for member in [*setup.heroes, *setup.monsters]
    )
    return swallowed < action.max_swallowed


def apply_swallowed(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    action: SwallowAction,
    event: BattleEvent,
) -> None:
    release_grapple(target.state, attacker.combatant_id)
    target.state.swallowed = SwallowedState(
        source_id=attacker.combatant_id, source_effect_id=action.id,
        damage_dice_count=action.damage_dice_count, damage_dice_size=action.damage_dice_size,
        damage_bonus=action.damage_bonus, damage_type=action.damage_type,
        regurgitation_damage_threshold=action.regurgitation_damage_threshold,
        regurgitation_save_ability=action.regurgitation_save_ability,
        regurgitation_save_dc=action.regurgitation_save_dc,
        regurgitation_range_ft=action.regurgitation_range_ft,
        exit_movement_ft=action.exit_movement_ft, exit_prone=action.exit_prone,
    )
    event.applied_condition_ids = list(dict.fromkeys([
        *event.applied_condition_ids, "blinded", "restrained", "swallowed",
    ]))
    event.feature_id = action.id
    event.description += f" {target.state.template.name} is swallowed."


def resolve_on_hit_swallow(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    event: BattleEvent,
    setup: EncounterSetup | None,
    dice,
) -> None:
    action = _action_for_attack(attacker, attack)
    if action is None or setup is None or not event.hit or target.state.is_dead or not target.state.is_alive:
        return
    if target.state.swallowed is not None or not size_at_most(target.state.template.size, action.max_target_size):
        return
    if not _capacity_available(attacker, setup, action):
        return
    roll, succeeded = resolve_saving_throw(
        target.state, action.on_hit_save_ability, action.on_hit_save_dc, dice,
    )
    event.saving_throw_roll = roll
    event.save_ability = action.on_hit_save_ability
    event.save_dc = action.on_hit_save_dc
    event.save_succeeded = succeeded
    if not succeeded:
        apply_swallowed(attacker, target, action, event)
