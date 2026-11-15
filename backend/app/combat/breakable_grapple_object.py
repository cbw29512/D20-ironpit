"""External breakable appendage attached to an ordinary source Grapple.

Damage the per-target object, not its owner; destruction releases only that
source's Grapple while the shared grapple cleanup owns all conditions.
"""
from __future__ import annotations

import logging

from app.combat.breakable_object_damage import damage_breakable_object_state
from app.combat.grapple_appendage_capacity import record_broken_grapple_appendage
from app.combat.grapple import release_grapple
from app.domain.models import CombatantState, GrappleSource
from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def damage_breakable_grapple_object(
    target: CombatantState,
    grapple: GrappleSource,
    attack_total: int,
    rolled_damage: int,
    damage_type: str,
    setup: EncounterSetup,
) -> tuple[int, bool]:
    try:
        if grapple not in target.grapple_sources or grapple.breakable_object is None:
            raise ValueError("The target has no active breakable Grapple object.")
        if setup is None or not grapple.linked_effect_id:
            raise ValueError("Breakable Grapple damage requires the linked source and encounter.")
        dealt, destroyed = damage_breakable_object_state(
            grapple.breakable_object, attack_total, rolled_damage, damage_type,
        )
        if destroyed:
            record_broken_grapple_appendage(setup, grapple.source_id, grapple.linked_effect_id)
            release_grapple(target, grapple.source_id)
        return dealt, destroyed
    except Exception:
        logger.exception("Failed to damage a breakable Grapple object on %s.", target.template.name)
        raise
