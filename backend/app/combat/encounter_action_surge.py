from __future__ import annotations

from app.combat.action_surge import action_surge_available, use_action_surge
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.policy import select_weapon_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_action_surge_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Iron Pit policy: spend Action Surge only when its extra Action can immediately Attack."""
    if not action_surge_available(attacker.state, turn_key):
        return [], sequence
    target = select_nearest_target(attacker, setup)
    if target is None:
        return [], sequence
    distance = combatant_distance(attacker, target)
    attack = select_weapon_attack(attacker.state, distance)
    if attack is None:
        return [], sequence

    events = [use_action_surge(sequence, round_number, attacker.combatant_id, attacker.state, turn_key)]
    sequence += 1
    if attacker.state.template.attack_action is not None:
        more, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
        events.extend(more)
        return events, sequence

    pack = pack_tactics_active(attacker, target, setup)
    events.append(resolve_encounter_attack(
        sequence, round_number, attacker, target, attack, distance, dice, setup,
        advantage_sources=1 if pack else 0, feature_id="action-surge",
    ))
    return events, sequence + 1
