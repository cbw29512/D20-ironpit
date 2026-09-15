from __future__ import annotations

import re

from app.domain.forced_movement_actions import ForcedMovementAction


def forced_movement_action_issues(action: ForcedMovementAction, actions: str) -> list[str]:
    """Verify no-roll forced movement actions against SRD action text."""
    try:
        if action.target_mode != "creatures_grappled_by_self":
            return [f"forced-movement-target-mode-mismatch:{action.id}"]
        direction = "toward" if action.direction == "toward_source" else "away from"
        target = r"each\s+creature\s+grappled\s+by\s+(?:it|the\s+[a-z -]+)"
        movement = rf"up\s+to\s+{action.distance_ft}\s*(?:ft\.?|feet)\s+straight\s+{direction}"
        heading = rf"\b{re.escape(action.name)}\b\s*\.\s*"
        named = re.search(rf"{heading}[^.]*{target}[^.]*{movement}", actions, re.IGNORECASE)
        return [] if named else [f"forced-movement-action-mismatch:{action.id}"]
    except Exception as exc:
        raise RuntimeError(f"Forced-movement source audit failed for {action.id}.") from exc
