from __future__ import annotations

import logging

from app.combat.ongoing_damage import resolve_ongoing_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_grapple_periodic_damage(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve periodic damage owned by active grapple-producing save actions."""
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        events: list[BattleEvent] = []
        for grapple in target.state.grapple_sources:
            if grapple.source_effect_id is None:
                continue
            source = members.get(grapple.source_id)
            if source is None or source.state.is_dead or not source.state.is_alive:
                continue
            action = next(
                (
                    item for item in source.state.template.saving_throw_actions
                    if item.id == grapple.source_effect_id
                ),
                None,
            )
            if action is None or action.grapple_periodic_damage is None:
                continue
            periodic = action.grapple_periodic_damage
            if periodic.timing != "target_turn_start":
                continue
            events.append(resolve_ongoing_damage(
                sequence,
                round_number,
                source,
                target,
                setup,
                dice,
                feature_id=action.id,
                feature_name=action.name,
                dice_count=periodic.dice_count,
                dice_size=periodic.dice_size,
                damage_bonus=periodic.damage_bonus,
                damage_type=periodic.damage_type,
                animation="grapple-periodic-damage",
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed grapple periodic damage for %s.", target.combatant_id)
        raise RuntimeError("Grapple periodic damage resolution failed.") from exc
