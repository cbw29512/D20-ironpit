"""Generic owner-linked grapple damage packets; no effect survives release or escape."""
from __future__ import annotations

import logging

from app.combat.dice import roll_dice
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def grapple_turn_start_damage(
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> list[tuple[str, int, str]]:
    """Evaluate only active grapple sources on this victim at their turn start."""
    try:
        members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        packets = []
        for source in member.state.grapple_sources:
            spec = source.periodic_damage
            if spec is None:
                continue
            grappler = members.get(source.source_id)
            if grappler is None or grappler.state.is_dead or grappler.state.is_unconscious:
                continue
            if not grappler.state.is_alive or grappler.state.current_hp <= 0:
                continue
            if abs(grappler.position_ft - member.position_ft) > source.range_ft:
                continue
            if not member.state.is_alive or member.state.is_dead:
                break
            total = roll_dice(dice, spec.dice_count, spec.dice_size)
            packets.append((spec.source_name, total, spec.damage_type))
        return packets
    except Exception:
        logger.exception("Failed to resolve grapple-linked start-of-turn damage for %s.", member.combatant_id)
        raise
