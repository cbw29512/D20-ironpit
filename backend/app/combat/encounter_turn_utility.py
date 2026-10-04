from __future__ import annotations

import logging

from app.combat.emanation_speed import sync_emanation_speed
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.persistent_save_zone_cast import choose_save_zone_action, cast_save_zone
from app.combat.suppression_zone_cast import (
    choose_suppression_zone_action,
    cast_suppression_zone,
)
from app.combat.teleport_policy import choose_teleport_action
from app.combat.teleport_resolution import resolve_teleport
from app.combat.timed_self_buffs import choose_timed_self_buff_action, resolve_timed_self_buff
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_control_support(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Cast Dimension Door, Spirit Guardians, or Silence when the action is still free."""
    try:
        events: list[BattleEvent] = []
        teleport = choose_teleport_action(member, setup, turn_key)
        if teleport is not None:
            action, destination = teleport
            moved, sequence = resolve_teleport(
                sequence, round_number, member, setup, action, destination, dice, turn_key,
            )
            events.extend(moved)
            return events, sequence
        self_buff = choose_timed_self_buff_action(member, setup, turn_key=turn_key)
        if self_buff is not None:
            events.append(resolve_timed_self_buff(
                sequence,
                round_number,
                member,
                self_buff,
                affected_states=[entry.state for entry in [*setup.heroes, *setup.monsters]],
                setup=setup,
                turn_key=turn_key,
                dice=dice,
            ))
            sequence += 1
            sync_friendly_save_auras(setup)
            sync_emanation_speed(setup)
            return events, sequence
        save_zone = choose_save_zone_action(member, setup, turn_key)
        if save_zone is not None:
            action, center = save_zone
            moved, sequence = cast_save_zone(
                sequence, round_number, member, setup, action, center, turn_key, dice,
            )
            events.extend(moved)
            return events, sequence
        zone = choose_suppression_zone_action(member, setup, turn_key)
        if zone is not None:
            action, center = zone
            event, sequence = cast_suppression_zone(
                sequence, round_number, member, setup, action, center, turn_key,
            )
            events.append(event)
        return events, sequence
    except Exception:
        logger.exception("Failed control-support stage for %s.", member.combatant_id)
        raise
