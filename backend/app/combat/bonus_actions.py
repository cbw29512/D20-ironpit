from __future__ import annotations

import logging

from app.combat.conditions import require_activity
from app.combat.dice import DiceProvider
from app.combat.disengage import take_disengage_action
from app.combat.stealth import take_hide_action
from app.domain.models import BattleEvent, BattlefieldState, CombatantState

logger = logging.getLogger(__name__)
NIMBLE_ESCAPE = "nimble-escape"


def _validate_nimble_escape(actor: CombatantState) -> None:
    try:
        if NIMBLE_ESCAPE not in actor.template.bonus_action_features:
            raise ValueError("Combatant does not have Nimble Escape.")
        require_activity(actor, "Bonus Action")
        if not actor.bonus_action_available:
            raise ValueError("Bonus Action is not available.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Nimble Escape validation failed for %s.", actor.template.name)
        raise RuntimeError("Nimble Escape could not be validated.") from exc


def use_nimble_escape_disengage(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
) -> BattleEvent:
    try:
        _validate_nimble_escape(actor)
        event = take_disengage_action(
            sequence,
            round_number,
            actor,
            battlefield,
            spend_action=False,
            feature_id=NIMBLE_ESCAPE,
        )
        actor.bonus_action_available = False
        event.description = (
            f"{actor.template.name} uses Nimble Escape to take the Disengage action."
        )
        return event
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Nimble Escape failed for %s.", actor.template.name)
        raise RuntimeError("Nimble Escape could not be resolved.") from exc


def use_nimble_escape_hide(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    battlefield: BattlefieldState,
    dice: DiceProvider,
) -> BattleEvent:
    try:
        _validate_nimble_escape(actor)
        event = take_hide_action(
            sequence,
            round_number,
            actor,
            battlefield,
            dice,
            spend_action=False,
            feature_id=NIMBLE_ESCAPE,
        )
        actor.bonus_action_available = False
        return event
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Nimble Escape Hide failed for %s.", actor.template.name)
        raise RuntimeError("Nimble Escape Hide could not be resolved.") from exc
