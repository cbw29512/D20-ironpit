from __future__ import annotations

import logging

from app.combat.emanation_save_damage import resolve_emanation_hit
from app.combat.emanation_speed import sync_emanation_speed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_emanation_entries(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve enter-or-start emanations when a creature steps into an area."""
    try:
        events: list[BattleEvent] = []
        sync_emanation_speed(setup)
        if not mover.state.is_alive or mover.state.is_dead:
            return events, sequence
        for source in [*setup.heroes, *setup.monsters]:
            if source.side == mover.side:
                continue
            active_ids = {
                effect.source_effect_id
                for effect in source.state.timed_effects
                if effect.source_id == source.combatant_id and effect.source_effect_id
            }
            for action in source.state.template.timed_self_buff_actions:
                emanation = action.start_turn_emanation_damage
                if action.id not in active_ids or emanation is None:
                    continue
                if emanation.trigger != "enter_or_start":
                    continue
                event, sequence = resolve_emanation_hit(
                    sequence, round_number, source, mover, action, setup, dice, turn_key,
                )
                if event is not None:
                    events.append(event)
        return events, sequence
    except Exception:
        logger.exception("Emanation entry resolution failed for %s.", mover.combatant_id)
        raise
