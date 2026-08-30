from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.attacks import resolve_attack
from app.combat.charge import resolve_charge_closing
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.policy import weapon_attack_profiles
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttackKind

DODGE_EFFECT_ID = "dodge"
MELEE_BRAWL_DISTANCE_FT = 5


def _legal_ranged_attack(attacker: EncounterCombatant, distance_ft: int):
    for attack in weapon_attack_profiles(attacker.state):
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.RANGED:
            if weapon.long_range_ft is not None and distance_ft <= weapon.long_range_ft:
                return attack
    return None


def _reachable_melee_distance(attacker: EncounterCombatant, distance_ft: int) -> int | None:
    if attacker.state.movement_remaining_ft <= 0:
        return None
    for attack in weapon_attack_profiles(attacker.state):
        if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
            continue
        reach = attack.weapon.reach_ft
        if distance_ft > reach and distance_ft - reach <= attacker.state.movement_remaining_ft:
            return reach
    return None


def _take_dodge(sequence: int, round_number: int, attacker: EncounterCombatant) -> BattleEvent:
    spend(attacker.state, "action")
    if DODGE_EFFECT_ID not in attacker.state.active_effect_ids:
        attacker.state.active_effect_ids.append(DODGE_EFFECT_ID)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
        feature_id=DODGE_EFFECT_ID, animation="dodge",
        description=f"{attacker.state.template.name} Dodges while closing to melee.",
    )


def resolve_simple_closing(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
    setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], int, bool]:
    """Reach melee this turn when possible; otherwise use legal ranged offense/Dodge while closing."""
    distance = combatant_distance(attacker, target)
    if distance <= MELEE_BRAWL_DISTANCE_FT:
        return [], sequence, False

    charge_events, charge_sequence, charged = resolve_charge_closing(
        sequence, round_number, attacker, target, dice, setup,
    )
    if charged:
        return charge_events, charge_sequence, True
    if attacker.state.template.attack_action is not None:
        return [], sequence, False

    melee_distance = _reachable_melee_distance(attacker, distance)
    if melee_distance is not None:
        movement_events, sequence, movement = move_toward_with_reactions(
            sequence, round_number, attacker, target, setup, melee_distance, dice,
        )
        if attacker.state.is_dead or attacker.state.is_unconscious:
            return movement_events, sequence, True
        if movement is not None and combatant_distance(attacker, target) <= melee_distance:
            return movement_events, sequence, False

    events: list[BattleEvent] = []
    ranged = _legal_ranged_attack(attacker, combatant_distance(attacker, target))
    if ranged is not None and is_available(attacker.state, "action"):
        close_enemy = close_ranged_threat_exists(attacker, setup) if setup is not None else True
        events.append(resolve_attack(
            sequence, round_number, attacker.state, target.state, ranged,
            combatant_distance(attacker, target), dice,
            actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
            close_enemy_active=close_enemy,
        ))
        sequence += 1
    elif is_available(attacker.state, "action"):
        events.append(_take_dodge(sequence, round_number, attacker))
        sequence += 1

    movement_events, sequence, _ = move_toward_with_reactions(
        sequence, round_number, attacker, target, setup, MELEE_BRAWL_DISTANCE_FT, dice,
    )
    events.extend(movement_events)
    return events, sequence, True
