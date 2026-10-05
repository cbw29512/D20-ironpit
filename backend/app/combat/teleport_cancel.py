from __future__ import annotations

import logging

from app.combat.grapple import release_grapple
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.encounters import EncounterCombatant
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def teleport_cancelable_effect_ids(state: CombatantState) -> list[str]:
    """Return active effect ids a teleport would cancel without changing position."""
    try:
        ids = [
            effect.effect_id
            for effect in state.timed_effects
            if effect.ends_on_teleport or effect.ground_contact
        ]
        if state.grapple_sources:
            ids.append("grappled")
            if any(source.restrains for source in state.grapple_sources):
                ids.append("restrained")
        unique: list[str] = []
        for effect_id in ids:
            if effect_id not in unique:
                unique.append(effect_id)
        return unique
    except Exception:
        logger.exception("Failed teleport-cancel inventory for %s.", state.template.name)
        raise


def clear_teleport_cancelable_effects(combatant: EncounterCombatant) -> list[str]:
    """Remove teleport-cancelable holds in place. Position is owned by the caller."""
    try:
        removed: list[str] = []
        for effect in list(combatant.state.timed_effects):
            if not (effect.ends_on_teleport or effect.ground_contact):
                continue
            for condition_id in remove_effect_group(combatant.state, effect):
                if condition_id not in removed:
                    removed.append(condition_id)
        for source in list(combatant.state.grapple_sources):
            release_grapple(combatant.state, source.source_id)
            if "grappled" not in removed:
                removed.append("grappled")
            if source.restrains and "restrained" not in removed:
                removed.append("restrained")
        return removed
    except Exception:
        logger.exception("Failed in-place teleport cancel for %s.", combatant.combatant_id)
        raise
