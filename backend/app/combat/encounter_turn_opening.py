from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.deferred_save_effect import cleanup_deferred_effects
from app.combat.feature_activation_phase import resolve_feature_activation_phase
from app.combat.fighter import use_second_wind
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.ongoing_spell_control import build_forced_retreat_event, forced_retreat_active
from app.combat.orc import should_use_adrenaline_rush, use_adrenaline_rush
from app.combat.paladin_auras_2014 import sync_paladin_auras_2014
from app.combat.policy import should_use_second_wind
from app.combat.start_turn import begin_turn_with_events
from app.combat.tactical_shift import resolve_tactical_shift
from app.combat.timed_effect_control import suppresses_voluntary_turn
from app.combat.encounter_turn_support import resolve_support_actions
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_turn_opening(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int, str, bool, bool]:
    """Resolve start-of-turn maintenance and pre-action automatic choices."""
    try:
        events: list[BattleEvent] = []
        cleanup_deferred_effects(setup)
        cleanup_grapples(setup)
        sync_paladin_auras_2014(setup)
        sync_friendly_save_auras(setup)

        start_events, sequence = begin_turn_with_events(
            sequence, round_number, attacker.combatant_id, attacker.state, dice,
        )
        events.extend(start_events)
        turn_key = f"{round_number}:{attacker.combatant_id}"

        if suppresses_voluntary_turn(attacker.state):
            return events, sequence, turn_key, True, False

        if forced_retreat_active(attacker.state):
            events.append(
                build_forced_retreat_event(
                    sequence, round_number, attacker.combatant_id, attacker.state,
                )
            )
            return events, sequence + 1, turn_key, True, False

        support_events, sequence = resolve_support_actions(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(support_events)
        if is_incapacitated(attacker.state):
            return events, sequence, turn_key, True, True

        activation_events, sequence = resolve_feature_activation_phase(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(activation_events)

        if should_use_second_wind(attacker.state):
            events.append(
                use_second_wind(
                    sequence, round_number, attacker.state, dice, attacker.combatant_id,
                )
            )
            sequence += 1
            shift_event = resolve_tactical_shift(
                sequence, round_number, attacker, setup,
            )
            if shift_event is not None:
                events.append(shift_event)
                sequence += 1

        if should_escape_grapple(attacker.state):
            events.append(
                resolve_escape_grapple(
                    sequence,
                    round_number,
                    attacker.combatant_id,
                    attacker.state,
                    dice,
                    encounter_actor=attacker,
                    setup=setup,
                )
            )
            return events, sequence + 1, turn_key, True, True

        if should_use_adrenaline_rush(attacker.state):
            adrenaline_event = use_adrenaline_rush(
                sequence, round_number, attacker.state, attacker.combatant_id,
            )
            if adrenaline_event is not None:
                events.append(adrenaline_event)
                sequence += 1

        return events, sequence, turn_key, False, True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Turn opening failed for %s.", attacker.combatant_id)
        raise RuntimeError("Combat turn opening could not be resolved.") from exc
