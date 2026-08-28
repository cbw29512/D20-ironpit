from __future__ import annotations

import logging
from collections.abc import Iterable

from app.combat.conditions import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.rolls import resolve_roll_mode, roll_d20
from app.domain.models import BattleEvent, CombatantState, ConditionKind

logger = logging.getLogger(__name__)


def roll_initiative_order(
    states: Iterable[CombatantState],
    dice: DiceProvider,
    sequence: int = 1,
    surprised_actor_ids: set[str] | None = None,
) -> tuple[list[BattleEvent], list[CombatantState], int]:
    try:
        surprised = surprised_actor_ids or set()
        combatants = list(states)
        events: list[BattleEvent] = []
        for state in combatants:
            invisible = ConditionKind.INVISIBLE in state.conditions
            is_surprised = state.template.id in surprised
            incapacitated = is_incapacitated(state)
            mode = resolve_roll_mode(
                int(invisible), int(is_surprised) + int(incapacitated)
            )
            initiative = roll_d20(dice, state.template.initiative_bonus, mode)
            state.initiative_roll = initiative.selected_roll
            state.initiative_total = initiative.total

            reasons = []
            if invisible:
                reasons.append("Invisible grants Advantage")
            if is_surprised:
                reasons.append("Surprise imposes Disadvantage")
            if incapacitated:
                reasons.append("Incapacitated imposes Disadvantage")
            detail = f" ({'; '.join(reasons)})" if reasons else ""
            events.append(BattleEvent(
                sequence=sequence,
                round_number=0,
                event_type="initiative",
                actor_id=state.template.id,
                actor_name=state.template.name,
                attack_roll=initiative,
                feature_id="surprise" if is_surprised else None,
                animation="initiative",
                description=(
                    f"{state.template.name} rolls initiative "
                    f"{state.initiative_total}{detail}."
                ),
            ))
            sequence += 1

        order = sorted(
            combatants,
            key=lambda state: (state.initiative_total or 0, state.template.initiative_bonus),
            reverse=True,
        )
        return events, order, sequence
    except Exception as exc:
        logger.exception("Initiative resolution failed.")
        raise RuntimeError("Initiative could not be resolved.") from exc
