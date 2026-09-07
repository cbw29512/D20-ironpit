from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.dice import DiceProvider
from app.combat.opening_burst import opening_feature_id
from app.combat.pit_policy import choose_standard_attack
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.combat.steady_aim import use_steady_aim
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_standard_turn_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve one ordinary Attack-action path plus universal Advantage sources."""
    choice = choose_standard_attack(attacker, setup)
    if choice is None or not is_available(attacker.state, "action"):
        return [], sequence
    target, attack, distance = choice
    events: list[BattleEvent] = []
    pack = pack_tactics_active(attacker, target, setup)
    steady = use_steady_aim(sequence, round_number, attacker.combatant_id, attacker.state)
    if steady is not None:
        events.append(steady)
        sequence += 1
    feature = opening_feature_id(round_number, attacker, setup)
    if feature is None:
        feature = "steady-aim" if steady is not None else ("pack-tactics" if pack else None)
    more, sequence = resolve_standard_attack_action(
        sequence, round_number, attacker, target, attack, distance, dice, setup, turn_key,
        advantage_sources=int(pack) + int(steady is not None), feature_id=feature,
    )
    events.extend(more)
    return events, sequence
