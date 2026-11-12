"""2014 Misty Step source proof using the shared in-place teleport-cancel primitive.

The Iron Pit never relocates a combatant. Misty Step is selected only when
an active teleport-cancelable restraint/hold can be removed.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_fog_cloud_2014 import source_proven_innate_fog_cloud_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.domain.teleport_actions import TeleportAction
from app.domain.combatants import ResourceDefinition
from app.domain.combatants import CombatantTemplate

logger = logging.getLogger(__name__)


def source_proven_innate_misty_step_2014(monster) -> list[TeleportAction]:
    """Bind only the exact, fully source-verified 3/day Cloud Giant Misty Step."""
    try:
        # The existing Fog Cloud proof validates the complete printed Cloud
        # Giant Innate Spellcasting clause and every parsed spell/use row.
        # Reuse that source proof; do not key combat behavior to monster name.
        if not source_proven_innate_fog_cloud_2014(monster):
            return []
        rows = [
            row for row in innate_spells_2014(monster)
            if row.get("id") == "misty-step"
        ]
        if len(rows) != 1:
            return []
        row = rows[0]
        if (
            row.get("name") != "misty step"
            or row.get("usage") != "per_day"
            or row.get("uses_per_day") != 3
            or row.get("shared_pool") is not False
            or row.get("qualifier") is not None
        ):
            return []
        return [TeleportAction(
            id="misty-step",
            name="Misty Step",
            level=2,
            action_cost="bonus_action",
            range_ft=30,
            resource_id="misty-step",
            resource_cost=1,
            expends_spell_slot=False,
            animation="misty-step",
            source="D&D Basic Rules 2014: Misty Step; Iron Pit in-place escape",
        )]
    except Exception:
        logger.exception("2014 innate Misty Step source proof failed for %s.", monster.id)
        raise
