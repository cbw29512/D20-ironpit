"""Observer-scoped tactile recognition for source-declared visual disguises."""
from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def recognize_visual_disguise_by_physical_inspection(
    observer: CombatantState,
    source: CombatantState,
    source_id: str,
) -> bool:
    """Record recognition when a qualifying direct tactile inspection occurs."""
    try:
        rule = source.template.visual_disguise_action
        if (
            rule is None
            or not rule.physical_inspection_inconsistent
            or not source.magical_visual_disguise_active
            or source.is_dead
            or not source.is_alive
            or source.current_hp <= 0
        ):
            return False
        recognized = observer.recognized_visual_disguise_source_ids
        if source_id in recognized:
            return False
        recognized.append(source_id)
        return True
    except Exception as exc:
        logger.exception(
            "Physical visual-disguise inspection failed for source %s.", source_id
        )
        raise RuntimeError(
            "Physical visual-disguise inspection could not be resolved."
        ) from exc
