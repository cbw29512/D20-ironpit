from __future__ import annotations

import logging
from collections.abc import Iterable

from app.combat.card_effects import attack_effect_change, dodge_effect_change
from app.combat.state import (
    begin_turn,
    end_turn,
    expire_attack_roll_effects_at_turn_start,
)
from app.domain.models import BattleEvent, CombatCardEffectChange, CombatantState

logger = logging.getLogger(__name__)


def _status_event(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    changes: list[CombatCardEffectChange],
) -> BattleEvent | None:
    if not changes:
        return None
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="status",
        actor_id=actor.template.id,
        actor_name=actor.template.name,
        effect_changes=changes,
        log_visible=False,
        animation="status",
        description="Combat-card effects update.",
    )


def begin_actor_turn(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    combatants: Iterable[CombatantState],
) -> tuple[list[BattleEvent], int]:
    try:
        roster = tuple(combatants)
        expired = expire_attack_roll_effects_at_turn_start(actor, roster)
        changes = [
            attack_effect_change(holder, effect, "remove")
            for holder, effect in expired
        ]
        if begin_turn(actor, roster):
            changes.append(dodge_effect_change(actor, "remove"))
        event = _status_event(sequence, round_number, actor, changes)
        return ([event], sequence + 1) if event else ([], sequence)
    except Exception as exc:
        logger.exception("Failed to begin reported turn for %s.", actor.template.name)
        raise RuntimeError("Turn-start reporting failed.") from exc


def end_actor_turn(
    sequence: int,
    round_number: int,
    actor: CombatantState,
    combatants: Iterable[CombatantState],
) -> tuple[list[BattleEvent], int]:
    try:
        expired = end_turn(actor, tuple(combatants))
        changes = [
            attack_effect_change(holder, effect, "remove")
            for holder, effect in expired
        ]
        event = _status_event(sequence, round_number, actor, changes)
        return ([event], sequence + 1) if event else ([], sequence)
    except Exception as exc:
        logger.exception("Failed to end reported turn for %s.", actor.template.name)
        raise RuntimeError("Turn-end reporting failed.") from exc
