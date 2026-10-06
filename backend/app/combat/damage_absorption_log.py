from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def damage_absorption_description(components: list[Any], defender_name: str) -> str:
    """Describe source-tagged typed damage replacement without source-name dispatch."""
    try:
        pieces = []
        for component in components or []:
            source_name = getattr(component, "absorption_source_name", None)
            if not source_name:
                continue
            healed = getattr(component, "absorbed_healing", 0) or 0
            pieces.append(
                f" {defender_name}'s {source_name} absorbs the "
                f"{component.damage_type.value} damage and restores {healed} HP."
            )
        return "".join(pieces)
    except Exception as exc:
        logger.exception("Failed to describe damage absorption for %s.", defender_name)
        raise RuntimeError("Damage absorption description could not be built.") from exc
