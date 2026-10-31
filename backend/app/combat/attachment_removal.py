"""Action and movement-based removal of any source-target attachment link."""
from __future__ import annotations

import logging

from app.combat.action_economy import claim_voluntary_activity, is_available, spend
from app.combat.attachments import detach_link
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def remove_attachment_by_action(
    setup: EncounterSetup, actor: EncounterCombatant,
    source_id: str, effect_id: str,
) -> bool:
    """A creature near the source may spend one ordinary Action to remove its link."""
    try:
        row = next((link for link in setup.attachments
                    if (link.source_id, link.effect_id) == (source_id, effect_id)), None)
        if row is None:
            return False
        if not row.action_removable or not is_available(actor.state, "action"):
            return False
        source = next((member for member in [*setup.heroes, *setup.monsters]
                       if member.combatant_id == source_id), None)
        if source is None:
            raise ValueError("Cannot remove link for an absent source.")
        if (actor.combatant_id != row.target_id
                and combatant_distance(actor, source) > row.action_removal_range_ft):
            return False
        spend(actor.state, "action")
        setup.attachments = list(detach_link(tuple(setup.attachments), source_id, effect_id))
        logger.info("%s spends Action to remove %s.", actor.combatant_id, row.source_name)
        return True
    except Exception:
        logger.exception("Action detachment failed for %s / %s.", source_id, effect_id)
        raise


def detach_attachment_with_movement(
    setup: EncounterSetup, actor: EncounterCombatant, effect_id: str,
) -> bool:
    """Source can spend its printed movement cost; does not grant free movement."""
    try:
        row = next((link for link in setup.attachments
                    if (link.source_id, link.effect_id) == (actor.combatant_id, effect_id)), None)
        if row is None:
            return False
        cost = row.source_detach_movement_ft
        if cost <= 0 or actor.state.is_dead or not actor.state.is_alive:
            return False
        if actor.state.movement_remaining_ft < cost:
            return False
        from app.combat.action_economy import voluntary_activity_available
        if not voluntary_activity_available(actor.state, "movement"):
            return False
        claim_voluntary_activity(actor.state, "movement")
        actor.state.movement_remaining_ft -= cost
        setup.attachments = list(detach_link(tuple(setup.attachments), actor.combatant_id, effect_id))
        logger.info("%s spends %s ft movement to detach %s.",
                    actor.combatant_id, cost, row.source_name)
        return True
    except Exception:
        logger.exception("Source movement detachment failed for %s.", actor.combatant_id)
        raise
