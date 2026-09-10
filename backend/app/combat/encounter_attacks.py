from __future__ import annotations

from app.combat.ally_context import active_allies
from app.combat.attacks import resolve_attack
from app.combat.champion import apply_critical_closing_move
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.forced_movement import apply_attack_pull, apply_attack_push
from app.combat.frenzy import mark_reckless_use_while_raging
from app.combat.frightened import frightened_d20_disadvantage
from app.combat.reckless_attack import activate_reckless_attack
from app.combat.redirect_attack import select_redirect_ally, swap_redirect_positions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack


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
    fear_disadvantage = frightened_d20_disadvantage(attacker.state, setup) if setup is not None else 0
    event = resolve_attack(
        sequence, round_number, attacker.state, target.state, attack, distance_ft, dice,
        actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
        spend_action=spend_action, advantage_sources=advantage_sources,
        other_disadvantage_sources=other_disadvantage_sources + fear_disadvantage, feature_id=feature_id,
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
    actual_target = target
    if redirect is not None and event.target_id == redirect.combatant_id:
        swap_redirect_positions(target, redirect)
        actual_target = redirect
    movement_kind = None
    moved_ft = 0
    if event.hit and attack.push_target_away_ft > 0:
        movement_kind = "pushed"
        moved_ft = apply_attack_push(attacker, actual_target, attack, hit=True)
    elif event.hit and attack.pull_target_toward_ft > 0:
        movement_kind = "pulled"
        moved_ft = apply_attack_pull(attacker, actual_target, attack, hit=True)
    if moved_ft:
        before = event.distance_after_ft if event.distance_after_ft is not None else distance_ft
        after = combatant_distance(attacker, actual_target)
        event.distance_before_ft = before
        event.distance_after_ft = after
        event.description += (
            f" {actual_target.state.template.name} is {movement_kind} {moved_ft} feet."
            f" Target is {movement_kind} {moved_ft} ft. ({before} ft. to {after} ft.)."
        )
    return apply_critical_closing_move(attacker, setup, event)