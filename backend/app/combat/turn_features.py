from __future__ import annotations

import logging

from app.combat.barbarian import enter_rage
from app.combat.dice import DiceProvider
from app.combat.fighter import use_second_wind
from app.combat.policy import should_use_second_wind
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def _can_enter_rage(actor: CombatantState) -> bool:
    try:
        resource = next((item for item in actor.resources if item.id == "rage"), None)
        return bool(
            "rage" in actor.template.bonus_action_features
            and not actor.raging
            and not actor.template.wearing_heavy_armor
            and actor.bonus_action_available
            and resource
            and resource.current_uses > 0
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Rage policy for %s.", actor.template.name)
        raise RuntimeError("Rage policy could not be evaluated.") from exc


def apply_automatic_turn_features(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        if _can_enter_rage(actor):
            events.append(enter_rage(sequence, round_number, actor))
            sequence += 1
        if should_use_second_wind(actor):
            events.append(use_second_wind(sequence, round_number, actor, dice))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Automatic turn features failed for %s.", actor.template.name)
        raise RuntimeError("Automatic turn features could not be resolved.") from exc
