from __future__ import annotations

from app.combat.ally_context import active_allies
from app.combat.attacks import resolve_attack
from app.combat.champion import apply_critical_closing_move
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.forced_movement import push_away
from app.combat.frenzy import mark_reckless_use_while_raging
from app.combat.reckless_attack import activate_reckless_attack
from app.combat.redirect_attack import select_redirect_ally, swap_redirect_positions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack


def _event_target(event: BattleEvent, target: EncounterCombatant, setup: EncounterSetup | None) -> EncounterCombatant:
    if setup is None or event.target_id == target.combatant_id:
        return target
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == event.target_id),
        target,
    )


def _apply_on_hit_push(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    event: BattleEvent,
    setup: EncounterSetup | None,
) -> None:
    effect = attack.on_hit_save_effect
    if (
        effect is None or effect.failure_push_ft == 0 or setup is None
        or not event.hit or event.save_succeeded is not False
    ):
        return
    actual_target = _event_target(event, target, setup)
    moved = push_away(attacker, actual_target, effect.failure_push_ft, setup)
    if moved:
        event.description += f" {actual_target.state.template.name} is pushed {moved} feet away."


def resolve_encounter_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup | None,
    *,
    spend_action: bool = True,
    advantage_sources: int = 0,
    other_disadvantage_sources: int = 0,
    feature_id: str | None = None,
    turn_key: str | None = None,
    bonus_damage: BonusDamageSpec | None = None,
    close_enemy_active: bool | None = None,
    allow_reckless: bool = False,
    off_turn: bool = False,
) -> BattleEvent:
    reckless_started = allow_reckless and activate_reckless_attack(
        attacker.state, attack, attacker.combatant_id, round_number,
    )
    if reckless_started:
        mark_reckless_use_while_raging(attacker.state, turn_key)
    redirect = select_redirect_ally(target, setup) if setup is not None else None
    close_enemy = close_enemy_active
    if close_enemy is None:
        close_enemy = False if setup is not None else True
    affected_states = [member.state for member in [*setup.heroes, *setup.monsters]] if setup is not None else None
    sneak_ally = setup is not None and bool(active_allies(attacker, setup))
    event = resolve_attack(
        sequence, round_number, attacker.state, target.state, attack, distance_ft, dice,
        actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
        spend_action=spend_action, advantage_sources=advantage_sources,
        other_disadvantage_sources=other_disadvantage_sources, feature_id=feature_id,
        turn_key=turn_key, bonus_damage=bonus_damage, close_enemy_active=close_enemy,
        redirect_target=redirect.state if redirect is not None else None,
        redirect_target_event_id=redirect.combatant_id if redirect is not None else None,
        affected_states=affected_states, sneak_attack_ally_available=sneak_ally,
        off_turn=off_turn,
    )
    if reckless_started:
        event.description += f" {attacker.state.template.name} uses Reckless Attack."
        if event.feature_id is None:
            event.feature_id = "reckless-attack"
    if redirect is not None and event.target_id == redirect.combatant_id:
        swap_redirect_positions(target, redirect)
    _apply_on_hit_push(attacker, target, attack, event, setup)
    return apply_critical_closing_move(attacker, setup, event)