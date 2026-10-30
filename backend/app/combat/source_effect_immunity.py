from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def immunity_key(source_id: str, source_effect_id: str) -> str:
    try:
        return f"{source_id}:{source_effect_id}"
    except Exception as exc:
        logger.exception("Failed to build source-effect immunity key.")
        raise RuntimeError("Source-effect immunity key could not be built.") from exc


def has_source_effect_immunity(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
) -> bool:
    try:
        return immunity_key(source_id, source_effect_id) in state.source_effect_immunities
    except Exception as exc:
        logger.exception("Failed to inspect source-effect immunity for %s.", state.template.name)
        raise RuntimeError("Source-effect immunity could not be inspected.") from exc


def grant_source_effect_immunity(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
) -> str:
    try:
        key = immunity_key(source_id, source_effect_id)
        if key not in state.source_effect_immunities:
            state.source_effect_immunities.append(key)
        return key
    except Exception as exc:
        logger.exception("Failed to grant source-effect immunity for %s.", state.template.name)
        raise RuntimeError("Source-effect immunity could not be granted.") from exc


__all__ = [
    "grant_source_effect_immunity",
    "has_source_effect_immunity",
    "immunity_key",
]
