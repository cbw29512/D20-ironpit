from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant
from app.combat.encounter_targeting import combatant_distance
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, WeaponAttackKind

DODGE_EFFECT_ID = "dodge"
OPENING_VOLLEY_EFFECT_ID = "opening-volley-used"


def _opening_ranged_attack(attacker: EncounterCombatant, distance_ft: int):
    if OPENING_VOLLEY_EFFECT_ID in attacker.state.active_effect_ids:
        return None
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
    """Resolve Iron Pit's one-volley-or-Dodge approach for melee-primary combatants."""
    primary = attacker.state.template.weapon_attack.weapon
    if primary.attack_kind is not WeaponAttackKind.MELEE:
        return [], sequence, False
    if combatant_distance(attacker, target) <= primary.reach_ft:
        return [], sequence, False

    events: list[BattleEvent] = []
    ranged = _opening_ranged_attack(attacker, combatant_distance(attacker, target))
    if ranged is not None and attacker.state.action_available:
        attacker.state.active_effect_ids.append(OPENING_VOLLEY_EFFECT_ID)
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
        primary.reach_ft,
    )
    if movement is not None:
        events.append(movement)
        sequence += 1
    return events, sequence, True
