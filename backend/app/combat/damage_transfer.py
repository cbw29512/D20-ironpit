from __future__ import annotations

import logging

from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def resolve_damage_transfer(
    source: EncounterCombatant,
    amount: int,
    setup: EncounterSetup,
    dice,
) -> tuple[int, int]:
    """Split incoming damage per Damage Transfer: source keeps floor(half), victim takes remainder.

    Requires an attached victim (grappled by source). Applies canonical damage to victim once.
    Does not recurse. Returns (source_keeps, victim_takes).
    """
    try:
        if amount <= 0:
            return amount, 0
        # Find attached victim: one of the combatants that has this source in grapple_sources
        victim = None
        for member in [*setup.heroes, *setup.monsters]:
            if any(g.source_id == source.combatant_id for g in member.state.grapple_sources):
                victim = member
                break
        if victim is None or victim.state.is_dead:
            return amount, 0
        source_keeps = amount // 2
        victim_takes = amount - source_keeps
        if victim_takes > 0:
            apply_damage(
                victim.state,
                victim_takes,
                False,
                [],
                [m.state for m in [*setup.heroes, *setup.monsters]],
                setup=setup,
                dice=dice,
            )
        return source_keeps, victim_takes
    except Exception:
        logger.exception("Failed to resolve Damage Transfer for %s.", source.combatant_id)
        raise
