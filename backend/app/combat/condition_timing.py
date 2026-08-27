from __future__ import annotations

import logging

from app.domain.models import BattleEvent, CombatantState, ConditionExpiry

logger = logging.getLogger(__name__)


def _matches_turn_trigger(
    target: CombatantState,
    actor: CombatantState,
    expires_on: ConditionExpiry | None,
    phase: str,
    source_id: str | None,
) -> bool:
    if phase == "start":
        source_trigger = ConditionExpiry.SOURCE_TURN_START
        target_trigger = ConditionExpiry.TARGET_TURN_START
    elif phase == "end":
        source_trigger = ConditionExpiry.SOURCE_TURN_END
        target_trigger = ConditionExpiry.TARGET_TURN_END
    else:
        raise ValueError(f"Unsupported turn phase: {phase}")
    return (
        expires_on is source_trigger and source_id == actor.instance_id
    ) or (
        expires_on is target_trigger and target.instance_id == actor.instance_id
    )


def expire_turn_conditions(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    combatants: list[CombatantState],
    phase: str,
) -> list[BattleEvent]:
    try:
        events: list[BattleEvent] = []
        for target in combatants:
            retained = []
            for condition in target.conditions:
                if not _matches_turn_trigger(
                    target, actor, condition.expires_on, phase, condition.source_id
                ):
                    retained.append(condition)
                    continue
                events.append(BattleEvent(
                    sequence=sequence + len(events),
                    round_number=round_number,
                    event_type="condition",
                    actor_id=target.instance_id,
                    actor_name=target.template.name,
                    target_id=target.instance_id,
                    target_name=target.template.name,
                    condition=condition.condition,
                    condition_active=False,
                    feature_id="condition-expiry",
                    animation="condition-end",
                    description=(
                        f"{target.template.name}'s {condition.condition.value.title()} condition ends."
                    ),
                ))
            target.conditions = retained
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Condition expiry failed for %s turn %s.", actor.template.name, phase)
        raise RuntimeError("Condition expiry could not be resolved.") from exc
