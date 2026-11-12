from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.persistent_save_zones import PersistentSaveZoneState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def member_in_save_zone(
    member: EncounterCombatant, zone: PersistentSaveZoneState,
    setup: EncounterSetup | None = None,
) -> bool:
    try:
        if member.state.position is None:
            return False
        center = zone.position
        if zone.follows_source:
            if setup is None:
                return False
            source = next((actor for actor in [*setup.heroes, *setup.monsters]
                           if actor.combatant_id == zone.source_id), None)
            if source is None or source.state.position is None:
                return False
            center = source.state.position
        return footprint_distance_ft(
            member.state.position,
            member.state.template.size,
            center,
            CreatureSize.MEDIUM,
        ) <= zone.radius_ft
    except Exception:
        logger.exception("Failed save-zone occupancy check for %s.", member.combatant_id)
        raise



def sight_is_lightly_obscured(
    observer: EncounterCombatant,
    setup: EncounterSetup | None,
) -> bool:
    """Detect live zone-based light obscurity for ordinary sight Perception.

    This is not Blindness or Heavy Obscurement: it does not prevent seeing a
    target, and it never changes attack rolls.
    """
    try:
        if setup is None:
            return False
        owners = {
            actor.combatant_id: actor.state
            for actor in [*setup.heroes, *setup.monsters]
        }
        for zone in setup.save_zones:
            if not zone.lightly_obscured:
                continue
            if zone.concentration:
                owner = owners.get(zone.source_id)
                if (owner is None or owner.concentration is None
                        or owner.concentration.effect_id != zone.action_id):
                    continue
            if member_in_save_zone(observer, zone, setup):
                return True
        return False
    except Exception:
        logger.exception("Failed light-obscurity geometry check for %s.", observer.combatant_id)
        raise
