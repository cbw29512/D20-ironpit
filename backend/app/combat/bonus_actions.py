from __future__ import annotations

import logging

from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)
NIMBLE_ESCAPE = "nimble-escape"


def use_nimble_escape_disengage(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
) -> BattleEvent:
    """Use Nimble Escape to take Disengage as a Bonus Action."""
    try:
        if NIMBLE_ESCAPE not in actor.template.bonus_action_features:
            raise ValueError("Combatant does not have Nimble Escape.")
        if not actor.bonus_action_available:
            raise ValueError("Bonus Action is not available.")

        actor.bonus_action_available = False
        actor.disengaged = True
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="disengage",
            actor_id=actor.template.id,
            actor_name=actor.template.name,
            distance_before_ft=battlefield.distance_ft,
            distance_after_ft=battlefield.distance_ft,
            feature_id=NIMBLE_ESCAPE,
            animation="disengage",
            description=f"{actor.template.name} uses Nimble Escape to take the Disengage action.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Nimble Escape failed for %s.", actor.template.name)
        raise RuntimeError("Nimble Escape could not be resolved.") from exc
