from __future__ import annotations

from app.combat.action_surge import action_surge_available, use_action_surge
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import DiceProvider
from app.combat.pit_policy import choose_standard_attack, target_order
from app.combat.standard_attack_action import resolve_standard_attack_action
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
    """Iron Pit policy: spend Action Surge only when its extra Action can immediately attack."""
    if not action_surge_available(attacker.state, turn_key):
        return [], sequence

    choice = None
    if attacker.state.template.attack_action is None:
        choice = choose_standard_attack(attacker, setup)
        if choice is None:
            return [], sequence
    elif not target_order(attacker, setup):
        return [], sequence

    events = [use_action_surge(sequence, round_number, attacker.combatant_id, attacker.state, turn_key)]
    sequence += 1
    if attacker.state.template.attack_action is not None:
        more, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
        events.extend(more)
        return events, sequence

    assert choice is not None
    target, attack, distance = choice
    pack = pack_tactics_active(attacker, target, setup)
    more, sequence = resolve_standard_attack_action(
        sequence, round_number, attacker, target, attack, distance, dice, setup, turn_key,
        advantage_sources=1 if pack else 0, feature_id="action-surge",
    )
    events.extend(more)
    return events, sequence
