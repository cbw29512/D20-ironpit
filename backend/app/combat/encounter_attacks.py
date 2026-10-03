from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.ally_context import active_allies
from app.combat.attacks import resolve_attack
from app.combat.champion import apply_critical_closing_move
from app.combat.brutal_strike_effects import apply_brutal_strike_effects, select_brutal_strike_effects
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.frenzy import mark_reckless_use_while_raging
from app.combat.reckless_attack import activate_reckless_attack
from app.combat.post_hit_self_buffs import apply_triggered_post_hit_self_buff
from app.combat.redirect_attack import select_redirect_ally, swap_redirect_positions
from app.combat.targeting_wards import blocked_targeting_event, check_targeting_ward
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
    brutal_strike_effect_ids: tuple[str, ...] | None = None,
) -> BattleEvent:
    if brutal_strike_effect_ids is not None:
        select_brutal_strike_effects(attacker.state, brutal_strike_effect_ids)
    ward = check_targeting_ward(attacker, target, dice)
    if ward is not None and not ward.succeeded:
        if spend_action:
            spend(attacker.state, "action")
        return blocked_targeting_event(
            sequence, round_number, attacker, target, attack.weapon.name, ward,
        )
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
        off_turn=off_turn, reaction_setup=setup, reaction_roller=attacker,
    )
    if ward is not None:
        if event.saving_throw_roll is None:
            event.saving_throw_roll = ward.roll
            event.save_ability = ward.gate.save_ability
            event.save_dc = ward.gate.save_dc
            event.save_succeeded = True
        event.description += f" {attacker.state.template.name} succeeds against {ward.gate.source_effect_id}."
    if reckless_started:
        event.description += f" {attacker.state.template.name} uses Reckless Attack."
        if event.feature_id is None:
            event.feature_id = "reckless-attack"
    if redirect is not None and event.target_id == redirect.combatant_id:
        swap_redirect_positions(target, redirect)
    post_hit_buff = apply_triggered_post_hit_self_buff(
        sequence, round_number, attacker, setup, event,
    )
    if post_hit_buff is not None:
        event.description += f" {post_hit_buff} activates."
    effect_target = redirect if redirect is not None and event.target_id == redirect.combatant_id else target
    brutal_effects = apply_brutal_strike_effects(
        attacker, effect_target, setup, turn_key,
        round_number=round_number, requested=brutal_strike_effect_ids,
    )
    if brutal_effects:
        names = ", ".join(item.replace("-", " ").title() for item in brutal_effects)
        event.description += f" Brutal Strike applies {names}."
    return apply_critical_closing_move(attacker, setup, event)
