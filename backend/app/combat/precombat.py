from __future__ import annotations

import logging
from collections.abc import Iterable

from app.combat.dice import DiceProvider
from app.combat.stealth import take_hide_action
from app.domain.models import (
    BattleEvent,
    BattlefieldState,
    CombatantState,
    EncounterSetup,
)

logger = logging.getLogger(__name__)
PRECOMBAT_HIDE = "precombat-hide"


def resolve_precombat_setup(
    sequence: int,
    combatants: Iterable[CombatantState],
    battlefield: BattlefieldState,
    dice: DiceProvider,
    setup: EncounterSetup | None,
) -> tuple[list[BattleEvent], set[str], int]:
    try:
        if setup is None:
            return [], set(), sequence

        states = {state.template.id: state for state in combatants}
        events: list[BattleEvent] = []
        surprised_actor_ids: set[str] = set()

        for actor_id, plan in setup.plans_by_actor.items():
            actor = states.get(actor_id)
            if actor is None:
                raise ValueError(f"Unknown precombat actor: {actor_id}.")

            if plan.attempt_hide:
                events.append(
                    take_hide_action(
                        sequence,
                        0,
                        actor,
                        battlefield,
                        dice,
                        spend_action=False,
                        feature_id=PRECOMBAT_HIDE,
                    )
                )
                sequence += 1

            if not actor.hidden:
                continue
            for target_id in plan.ambush_target_ids:
                if target_id == actor_id:
                    raise ValueError("A combatant cannot ambush itself.")
                if target_id not in states:
                    raise ValueError(f"Unknown ambush target: {target_id}.")
                surprised_actor_ids.add(target_id)

        return events, surprised_actor_ids, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Precombat setup resolution failed.")
        raise RuntimeError("Precombat setup could not be resolved.") from exc
