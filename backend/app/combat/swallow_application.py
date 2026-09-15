from __future__ import annotations

from app.combat.grapple import release_grapple
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.size import size_at_most
from app.domain.swallow import SwallowAction, SwallowedState


def _action_for_attack(attacker: EncounterCombatant, attack: WeaponAttack) -> SwallowAction | None:
    effect = attack.on_hit_save_effect
    if effect is None or not effect.swallow_on_failure:
        return None
    return next(
        (
            action for action in attacker.state.template.swallow_actions
            if action.attack_id == attack.id and not action.requires_existing_grapple
        ),
        None,
    )


def capacity_available(attacker: EncounterCombatant, setup: EncounterSetup, action: SwallowAction) -> bool:
    if action.max_swallowed is None:
        return True
    swallowed = sum(
        int(member.state.swallowed is not None and member.state.swallowed.source_id == attacker.combatant_id)
        for member in [*setup.heroes, *setup.monsters]
    )
    return swallowed < action.max_swallowed


def apply_swallowed(
    attacker: EncounterCombatant, target: EncounterCombatant, action: SwallowAction, event: BattleEvent,
) -> None:
    release_grapple(target.state, attacker.combatant_id)
    target.state.swallowed = SwallowedState(
        source_id=attacker.combatant_id, source_effect_id=action.id,
        damage_dice_count=action.damage_dice_count, damage_dice_size=action.damage_dice_size,
        damage_bonus=action.damage_bonus, damage_type=action.damage_type,
        start_turn_save_ability=action.start_turn_save_ability, start_turn_save_dc=action.start_turn_save_dc,
        source_death_release=action.source_death_release,
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
    event.description += f" {target.state.template.name} is contained by {attacker.state.template.name}."


def resolve_on_hit_swallow(
    attacker: EncounterCombatant, target: EncounterCombatant, attack: WeaponAttack,
    event: BattleEvent, setup: EncounterSetup | None,
) -> None:
    action = _action_for_attack(attacker, attack)
    if action is None or setup is None or not event.hit or event.save_succeeded is not False:
        return
    if target.state.is_dead or not target.state.is_alive or target.state.swallowed is not None:
        return
    if not size_at_most(target.state.template.size, action.max_target_size):
        return
    if capacity_available(attacker, setup, action):
        apply_swallowed(attacker, target, action, event)
