from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.models import DiceRoll

logger = logging.getLogger(__name__)


def resolve_start_turn_timed_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider | None = None,
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
        feature_roll = None
        if action.start_turn_roll_die_size is not None:
            if dice is None:
                raise ValueError(f"{action.name} requires a dice provider for its start-turn trigger.")
            roll = dice.roll(action.start_turn_roll_die_size)
            feature_roll = DiceRoll(
                notation=f"1d{action.start_turn_roll_die_size}",
                rolls=[roll], selected_roll=roll, total=roll,
            )
            if roll < action.start_turn_roll_minimum:
                return BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="feature",
                    actor_id=member.combatant_id, actor_name=member.state.template.name,
                    target_id=member.combatant_id, target_name=member.state.template.name,
                    feature_id=action.id, feature_roll=feature_roll, animation=action.animation,
                    description=(
                        f"{member.state.template.name} rolls {roll} for {action.name}; "
                        "the buff does not activate."
                    ),
                )
        event = resolve_timed_self_buff(
            sequence,
            round_number,
            member,
            action,
            spend_action_cost=False,
            affected_states=[entry.state for entry in [*setup.heroes, *setup.monsters]],
        )
        if feature_roll is not None:
            event.feature_roll = feature_roll
            event.description = (
                f"{member.state.template.name} rolls {feature_roll.total} for "
                f"{action.name}; the buff activates."
            )
        return event
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Start-turn timed self-buff failed for %s.", member.combatant_id)
        raise RuntimeError("Start-turn timed self-buff could not be resolved.") from exc
