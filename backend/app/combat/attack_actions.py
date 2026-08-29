from __future__ import annotations

import logging

from app.combat.ally_context import pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant, take_encounter_dash
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.policy import preferred_distance_for_attacks, select_allowed_weapon_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _validate_slots(attacker: EncounterCombatant) -> None:
    definition = attacker.state.template.attack_action
    if definition is None:
        raise ValueError("Combatant has no multi-strike Attack action.")
    known = {
        attacker.state.template.weapon_attack.id,
        *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
    }
    for slot in definition.slots:
        unknown = set(slot.attack_ids) - known
        if unknown:
            raise ValueError(f"Unknown attack IDs in {definition.name}: {sorted(unknown)}")


def _prepare_first_slot(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    allowed_ids: list[str],
) -> tuple[list[BattleEvent], int, bool]:
    events: list[BattleEvent] = []
    attack = select_allowed_weapon_attack(attacker.state, combatant_distance(attacker, target), allowed_ids)
    if attack is not None:
        return events, sequence, True

    desired = preferred_distance_for_attacks(attacker.state, allowed_ids)
    movement = move_toward_combatant(sequence, round_number, attacker, target, desired)
    if movement is not None:
        events.append(movement)
        sequence += 1
    if select_allowed_weapon_attack(attacker.state, combatant_distance(attacker, target), allowed_ids):
        return events, sequence, True

    events.append(take_encounter_dash(sequence, round_number, attacker, target))
    sequence += 1
    movement = move_toward_combatant(sequence, round_number, attacker, target, desired)
    if movement is not None:
        events.append(movement)
        sequence += 1
    return events, sequence, False


def resolve_attack_action(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve a multi-strike Attack action with legal movement and retargeting between strikes."""
    try:
        _validate_slots(attacker)
        definition = attacker.state.template.attack_action
        if definition is None:
            raise ValueError("Combatant has no multi-strike Attack action.")
        if not attacker.state.action_available:
            raise ValueError("Action is not available.")

        target = select_nearest_target(attacker, setup)
        if target is None:
            return [], sequence
        events, sequence, can_attack = _prepare_first_slot(
            sequence, round_number, attacker, target, definition.slots[0].attack_ids
        )
        if not can_attack:
            return events, sequence

        attacker.state.action_available = False
        for slot in definition.slots:
            target = select_nearest_target(attacker, setup)
            if target is None:
                break
            distance = combatant_distance(attacker, target)
            attack = select_allowed_weapon_attack(attacker.state, distance, slot.attack_ids)
            if attack is None:
                desired = preferred_distance_for_attacks(attacker.state, slot.attack_ids)
                movement = move_toward_combatant(
                    sequence, round_number, attacker, target, desired
                )
                if movement is not None:
                    events.append(movement)
                    sequence += 1
                attack = select_allowed_weapon_attack(
                    attacker.state, combatant_distance(attacker, target), slot.attack_ids
                )
            if attack is None:
                continue
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
                spend_action=False,
                advantage_sources=1 if pack else 0,
                feature_id="pack-tactics" if pack else None,
            ))
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Attack action sequence failed for %s.", attacker.combatant_id)
        raise RuntimeError("Attack action sequence could not be resolved.") from exc
