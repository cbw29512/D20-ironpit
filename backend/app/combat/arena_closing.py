from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.charge import resolve_charge_closing
from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant
from app.combat.encounter_targeting import combatant_distance
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, WeaponAttackKind

DODGE_EFFECT_ID = "dodge"
MELEE_BRAWL_DISTANCE_FT = 5


def _legal_ranged_attack(attacker: EncounterCombatant, distance_ft: int):
    for attack in weapon_attack_profiles(attacker.state):
        weapon = attack.weapon
        if weapon.attack_kind is not WeaponAttackKind.RANGED:
            continue
        if weapon.long_range_ft is not None and distance_ft <= weapon.long_range_ft:
            return attack
    return None


def _take_dodge(sequence: int, round_number: int, attacker: EncounterCombatant) -> BattleEvent:
    attacker.state.action_available = False
    if DODGE_EFFECT_ID not in attacker.state.active_effect_ids:
        attacker.state.active_effect_ids.append(DODGE_EFFECT_ID)
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=attacker.combatant_id,
        actor_name=attacker.state.template.name,
        feature_id=DODGE_EFFECT_ID,
        animation="dodge",
        description=f"{attacker.state.template.name} Dodges while closing to melee.",
    )


def resolve_simple_closing(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int, bool]:
    """Resolve the flat-pit approach: use legal ranged offense while closing, never hold range."""
    if combatant_distance(attacker, target) <= MELEE_BRAWL_DISTANCE_FT:
        return [], sequence, False

    charge_events, charge_sequence, charged = resolve_charge_closing(
        sequence, round_number, attacker, target, dice,
    )
    if charged:
        return charge_events, charge_sequence, True

    # Multiattack/Extra Attack must keep its full printed action economy. The caller
    # resolves the Attack action first and then spends any remaining movement closing.
    if attacker.state.template.attack_action is not None:
        return [], sequence, False

    events: list[BattleEvent] = []
    ranged = _legal_ranged_attack(attacker, combatant_distance(attacker, target))
    if ranged is not None and attacker.state.action_available:
        events.append(resolve_attack(
            sequence,
            round_number,
            attacker.state,
            target.state,
            ranged,
            combatant_distance(attacker, target),
            dice,
            actor_event_id=attacker.combatant_id,
            target_event_id=target.combatant_id,
        ))
        sequence += 1
    elif attacker.state.action_available:
        events.append(_take_dodge(sequence, round_number, attacker))
        sequence += 1

    movement = move_toward_combatant(
        sequence,
        round_number,
        attacker,
        target,
        MELEE_BRAWL_DISTANCE_FT,
    )
    if movement is not None:
        events.append(movement)
        sequence += 1
    return events, sequence, True
