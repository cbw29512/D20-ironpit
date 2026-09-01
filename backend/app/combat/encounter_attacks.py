from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.champion import apply_critical_closing_move
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import close_ranged_threat_exists
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
) -> BattleEvent:
    redirect = select_redirect_ally(target, setup) if setup is not None else None
    close_enemy = close_enemy_active
    if close_enemy is None:
        close_enemy = close_ranged_threat_exists(attacker, setup) if setup is not None else True
    affected_states = [member.state for member in [*setup.heroes, *setup.monsters]] if setup is not None else None
    event = resolve_attack(
        sequence, round_number, attacker.state, target.state, attack, distance_ft, dice,
        actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
        spend_action=spend_action, advantage_sources=advantage_sources,
        other_disadvantage_sources=other_disadvantage_sources, feature_id=feature_id,
        turn_key=turn_key, bonus_damage=bonus_damage, close_enemy_active=close_enemy,
        redirect_target=redirect.state if redirect is not None else None,
        redirect_target_event_id=redirect.combatant_id if redirect is not None else None,
        affected_states=affected_states,
    )
    if redirect is not None and event.target_id == redirect.combatant_id:
        swap_redirect_positions(target, redirect)
    return apply_critical_closing_move(attacker, setup, event)
