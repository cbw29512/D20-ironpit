from __future__ import annotations

import logging

from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def take_disengage(
    sequence: int,
    round_number: int,
    actor: CombatantState,
) -> BattleEvent:
    """Spend the Action so the actor's movement does not provoke this turn."""
    try:
        if not actor.action_available:
            raise ValueError("Action is not available for Disengage.")
        actor.action_available = False
        actor.disengaged_this_turn = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="disengage",
            actor_id=actor.instance_id,
            actor_name=actor.template.name,
            feature_id="disengage",
            animation="disengage",
            description=f"{actor.template.name} takes the Disengage action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Disengage failed for %s.", actor.template.name)
        raise RuntimeError("Disengage could not be resolved.") from exc
