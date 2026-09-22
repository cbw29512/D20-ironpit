from __future__ import annotations

import logging

from app.combat.activation_movement import resolve_activation_movement
from app.combat.barbarian import enter_rage
from app.combat.paladin_auras_2014 import sync_paladin_auras_2014
from app.combat.stationary_attack_advantage import use_stationary_attack_advantage
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_feature_activation_phase(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve supported pre-action feature activations through shared declarative mechanics."""
    try:
        events: list[BattleEvent] = []
        focus_event = use_stationary_attack_advantage(
            sequence, round_number, attacker, setup, feature_id="steady-aim",
        )
        if focus_event is not None:
            events.append(focus_event)
            sequence += 1

        rage_event = enter_rage(sequence, round_number, attacker.state, attacker.combatant_id)
        if rage_event is None:
            return events, sequence
        events.append(rage_event)
        sequence += 1
        fraction = attacker.state.template.progression_features.instinctive_pounce_fraction
        if fraction <= 0:
            return events, sequence
        movement_events, sequence = resolve_activation_movement(
            sequence,
            round_number,
            attacker,
            setup,
            dice,
            speed_fraction=fraction,
            turn_key=turn_key,
        )
        events.extend(movement_events)
        sync_paladin_auras_2014(setup)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Feature activation phase failed for %s.", attacker.combatant_id)
        raise RuntimeError("Feature activation phase could not be resolved.") from exc
