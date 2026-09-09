from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.resources import resource_state
from app.domain.models import AuditPhase, AuditStep, BattleEvent, CombatantState, DiceRoll, EventAudit

logger = logging.getLogger(__name__)


def resolve_start_turn_recharges(
    sequence: int,
    round_number: int,
    combatant_id: str,
    state: CombatantState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve every printed Recharge X-6 resource at the start of this creature's turn."""
    try:
        events: list[BattleEvent] = []
        for definition in state.template.resources:
            rule = definition.recharge
            if rule is None:
                continue
            if rule.trigger != "start_of_turn":
                raise ValueError(f"Unsupported recharge trigger: {rule.trigger!r}.")
            runtime = resource_state(state, definition.id)
            before = runtime.current_uses
            rolled = dice.roll(rule.die_size)
            succeeded = rolled >= rule.minimum_roll
            if succeeded:
                runtime.current_uses = runtime.max_uses
            after = runtime.current_uses
            label = f"Recharge {rule.minimum_roll}-{rule.die_size}"
            if succeeded and after > before:
                result = f"{definition.name} recharges ({before}->{after})."
            elif succeeded:
                result = f"{definition.name} is already available."
            else:
                result = f"{definition.name} does not recharge."
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=combatant_id,
                actor_name=state.template.name,
                feature_id=f"recharge:{definition.id}",
                resource_roll=DiceRoll(
                    notation=f"1d{rule.die_size}",
                    rolls=[rolled],
                    selected_roll=rolled,
                    total=rolled,
                ),
                resource_remaining=after,
                animation="recharge",
                description=f"{state.template.name} rolls {rolled} for {label}. {result}",
                audit=EventAudit(steps=[
                    AuditStep(
                        phase=AuditPhase.ROLL,
                        kind="roll",
                        label=f"{definition.name} {label}: {rolled}",
                    ),
                    AuditStep(
                        phase=AuditPhase.RESOURCE_CHANGE,
                        kind="resource",
                        label=f"{definition.id}: {before}->{after}",
                    ),
                ]),
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed to resolve start-turn recharge for %s.", state.template.name)
        raise