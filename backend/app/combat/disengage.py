from __future__ import annotations

import logging

from app.combat.conditions import require_activity
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)
DISENGAGE = "disengage"


def take_disengage_action(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
    *,
    spend_action: bool = True,
    feature_id: str = DISENGAGE,
) -> BattleEvent:
    try:
        require_activity(actor, "Action" if spend_action else "Bonus Action")
        if spend_action and not actor.action_available:
            raise ValueError("Action is not available for Disengage.")
        if spend_action:
            actor.action_available = False
        actor.disengaged = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="disengage",
            actor_id=actor.template.id,
            actor_name=actor.template.name,
            distance_before_ft=battlefield.distance_ft,
            distance_after_ft=battlefield.distance_ft,
            feature_id=feature_id,
            animation="disengage",
            description=f"{actor.template.name} takes the Disengage action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Disengage failed for %s.", actor.template.name)
        raise RuntimeError("Disengage could not be resolved.") from exc
