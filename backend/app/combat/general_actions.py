from __future__ import annotations

import logging
from typing import Literal

from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def _can_bonus_disengage(actor: CombatantState, feature_id: str | None) -> bool:
    return any(
        grant.id == feature_id
        and grant.action_id == "disengage"
        and grant.action_cost == "bonus_action"
        for grant in actor.template.granted_actions
    )


def take_disengage(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    *,
    action_cost: Literal["action", "bonus_action"] = "action",
    feature_id: str | None = None,
) -> BattleEvent:
    """Take Disengage at its normal Action cost or a verified granted Bonus Action cost."""
    try:
        if action_cost == "action":
            if not actor.action_available:
                raise ValueError("Action is not available for Disengage.")
            actor.action_available = False
        else:
            if not _can_bonus_disengage(actor, feature_id):
                raise ValueError("Combatant is not granted Bonus Action Disengage.")
            if not actor.bonus_action_available:
                raise ValueError("Bonus Action is not available for Disengage.")
            actor.bonus_action_available = False

        actor.disengaged_this_turn = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="disengage",
            actor_id=actor.instance_id,
            actor_name=actor.template.name,
            feature_id=feature_id or "disengage",
            animation="disengage",
            description=(
                f"{actor.template.name} takes the Disengage action"
                f" using its {'Bonus Action' if action_cost == 'bonus_action' else 'Action'}."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Disengage failed for %s.", actor.template.name)
        raise RuntimeError("Disengage could not be resolved.") from exc
