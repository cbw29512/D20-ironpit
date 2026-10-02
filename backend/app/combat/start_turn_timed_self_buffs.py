from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def resolve_start_turn_timed_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Resolve the highest-priority legal self-buff whose source timing is start of turn."""
    try:
        if member.state.is_dead or not member.state.is_alive or member.state.current_hp <= 0:
            return None
        if is_incapacitated(member.state):
            return None
        action = choose_timed_self_buff_action(
            member,
            setup,
            activation_timing="start_turn",
        )
        if action is None:
            return None
        return resolve_timed_self_buff(
            sequence,
            round_number,
            member,
            action,
            spend_action_cost=False,
            affected_states=[entry.state for entry in [*setup.heroes, *setup.monsters]],
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Start-turn timed self-buff failed for %s.", member.combatant_id)
        raise RuntimeError("Start-turn timed self-buff could not be resolved.") from exc
