from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.domain.models import BattleEvent, CombatantState, DiceRoll
from app.domain.recharge import RechargeState

logger = logging.getLogger(__name__)


def get_recharge_state(actor: CombatantState, feature_id: str) -> RechargeState | None:
    return next((item for item in actor.recharges if item.feature_id == feature_id), None)


def require_recharge_available(actor: CombatantState, feature_id: str) -> None:
    state = get_recharge_state(actor, feature_id)
    if state is None:
        raise ValueError(f"Recharge state is missing for {feature_id}.")
    if not state.available:
        raise ValueError(f"{feature_id} has not recharged.")


def spend_recharge(actor: CombatantState, feature_id: str) -> None:
    require_recharge_available(actor, feature_id)
    state = get_recharge_state(actor, feature_id)
    if state is None:
        raise ValueError(f"Recharge state is missing for {feature_id}.")
    state.available = False


def roll_recharges(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    dice: DiceProvider,
) -> list[BattleEvent]:
    try:
        events: list[BattleEvent] = []
        for state in actor.recharges:
            if state.available:
                continue
            value = dice.roll(state.die_size)
            restored = state.min_roll <= value <= state.max_roll
            if restored:
                state.available = True
            roll = DiceRoll(
                notation=f"1d{state.die_size}",
                rolls=[value],
                selected_roll=value,
                total=value,
            )
            events.append(BattleEvent(
                sequence=sequence + len(events),
                round_number=round_number,
                event_type="recharge",
                actor_id=actor.instance_id,
                actor_name=actor.template.name,
                recharge_roll=roll,
                test_success=restored,
                feature_id=state.feature_id,
                animation="recharge",
                description=(
                    f"{actor.template.name} rolls {value} to recharge {state.feature_id}: "
                    f"{'recharged' if restored else 'not recharged'}."
                ),
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Recharge resolution failed for %s.", actor.template.name)
        raise RuntimeError("Recharge rolls could not be resolved.") from exc
