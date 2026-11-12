"""Shared browser serializer for generic spell-effect removal actions.

Both monster and hero cards must emit identical parameters so the one browser
effect-removal resolver can execute the same spell regardless of source.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def effect_removal_row(action: Any) -> dict[str, Any]:
    """Serialize only source-owned typed fields; no ability-name branching."""
    try:
        return {
            "id": action.id, "name": action.name, "level": action.level,
            "actionCost": action.action_cost, "range": action.range_ft,
            "castingAbility": action.casting_ability, "targetMode": action.target_mode,
            "autoRemoveMaxLevel": action.auto_remove_max_level,
            "effectTags": list(action.effect_tags),
            "resourceId": action.resource_id, "resourceCost": action.resource_cost,
            "expendsSpellSlot": action.expends_spell_slot, "animation": action.animation,
        }
    except Exception:
        logger.exception("Browser effect-removal serialization failed: %s", getattr(action, "id", "unknown"))
        raise
