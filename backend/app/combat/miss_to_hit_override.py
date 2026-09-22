from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_miss_to_hit_override(
    attacker: CombatantState,
    *,
    hit: bool,
) -> tuple[bool, str | None, str | None]:
    """Spend a declarative resource to turn a missed in-range attack into a normal hit."""
    try:
        if hit:
            return True, None, None
        resource_id = attacker.template.progression_features.miss_to_hit_override_resource_id
        if resource_id is None:
            return False, None, None
        resource = next((item for item in attacker.resources if item.id == resource_id), None)
        if resource is None:
            raise ValueError(f"Miss-to-hit override references missing resource {resource_id}.")
        if resource.current_uses <= 0:
            return False, None, None
        resource.current_uses -= 1
        return True, resource_id, resource.name
    except Exception as exc:
        logger.exception("Failed to resolve miss-to-hit override for %s.", attacker.template.name)
        raise RuntimeError("Miss-to-hit override could not be resolved.") from exc
