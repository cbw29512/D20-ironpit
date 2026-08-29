from __future__ import annotations

from app.combat.ally_context import pack_tactics_active
from app.combat.arena_closing import resolve_simple_closing
from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage, finalize_rage_turn
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.encounter_turns import prepare_encounter_attack
from app.combat.fighter import use_second_wind
from app.combat.orc import use_adrenaline_rush
from app.combat.policy import should_use_second_wind
from app.combat.state import begin_turn
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_combat_turn(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one living combatant turn through the canonical encounter rules."""
    events: list[BattleEvent] = []
    begin_turn(attacker.state)

    rage_event = enter_rage(
        sequence, round_number, attacker.state, attacker.combatant_id
    )
    if rage_event is not None:
        events.append(rage_event)
        sequence += 1

    if should_use_second_wind(attacker.state):
        events.append(use_second_wind(
            sequence, round_number, attacker.state, dice, attacker.combatant_id
        ))
        sequence += 1

    adrenaline_event = use_adrenaline_rush(
        sequence, round_number, attacker.state, attacker.combatant_id
    )
    if adrenaline_event is not None:
        events.append(adrenaline_event)
        sequence += 1

    closing_events, sequence, closing_handled = resolve_simple_closing(
        sequence, round_number, attacker, target, dice
    )
    events.extend(closing_events)

    if not closing_handled and attacker.state.template.attack_action is not None:
        action_events, sequence = resolve_attack_action(
            sequence, round_number, attacker, setup, dice
        )
        events.extend(action_events)
    elif not closing_handled:
        attack, prep_events, sequence = prepare_encounter_attack(
            sequence, round_number, attacker, target
        )
        events.extend(prep_events)
        if attack is not None:
            pack = pack_tactics_active(attacker, target, setup)
            events.append(resolve_attack(
                sequence,
                round_number,
                attacker.state,
                target.state,
                attack,
                combatant_distance(attacker, target),
                dice,
                actor_event_id=attacker.combatant_id,
                target_event_id=target.combatant_id,
                advantage_sources=1 if pack else 0,
                feature_id="pack-tactics" if pack else None,
            ))
            sequence += 1

    rage_event, sequence = finalize_rage_turn(
        sequence, round_number, attacker.state, attacker.combatant_id
    )
    if rage_event is not None:
        events.append(rage_event)
    return events, sequence
