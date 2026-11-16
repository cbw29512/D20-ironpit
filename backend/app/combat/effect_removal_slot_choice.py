"""Universal source-declared higher-slot choice for effect-removal spells.

State: actual slot resources, not printed action level, determine both payment
and automatic-dispel ceiling. Does not alter immutable creature templates.
"""
from __future__ import annotations

import logging

from app.combat.spellcasting import legal_slot_levels

logger = logging.getLogger(__name__)


def choose_effect_removal_slot(remover, action, turn_key, spell_levels=()):
    """Return (resource ID, cast level), or (None, None) if not castable."""
    try:
        if not action.upcast_slot_level:
            if action.resource_id is None:
                return None, action.auto_remove_max_level
            resource = next(
                (item for item in remover.state.resources
                 if item.id == action.resource_id and item.current_uses >= action.resource_cost),
                None,
            )
            return (
                (resource.id, action.auto_remove_max_level) if resource is not None
                else (None, None)
            )
        if not action.expends_spell_slot or not action.resource_id:
            raise ValueError("Upcast removal requires a source-defined spell slot.")
        legal = legal_slot_levels(
            remover.state, turn_key, action.level, higher_slot_scaling=True,
        )
        if not legal:
            return None, None
        # Preserve scarce slots: prefer the cheapest slot that automatically
        # ends the highest qualifying target spell within available capacity.
        affordable = [level for level in spell_levels if level <= max(legal)]
        needed = max(affordable, default=action.level)
        level = next((item for item in legal if item >= needed), legal[0])
        return f"spell-slot-{level}", level
    except Exception:
        logger.exception("Could not select actual effect-removal cast slot for %s", action.id)
        raise
