"""Source-neutral line-of-vision obstruction from fight-local zone projections.

A heavy-physical zone obstructs even Truesight; magical darkness does not.
This is NOT the Blinded condition: the zone affects a particular sight line.
"""
from __future__ import annotations

import logging

from app.domain.runtime import CombatantState
from app.domain.suppression_zones import PersistentSuppressionZoneState

logger = logging.getLogger(__name__)


def _line_crosses_zone(
    observer: CombatantState,
    target: CombatantState,
    zone: PersistentSuppressionZoneState,
) -> bool:
    """Test the shortest point-to-segment distance in grid-square units."""
    try:
        a, b = observer.position, target.position
        if a is None or b is None:
            # An active obstruction without a known sight line cannot be
            # assumed transparent; preserve the universal fail-closed gate.
            return True
        dx, dy = b.x - a.x, b.y - a.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            nearest_x, nearest_y = float(a.x), float(a.y)
        else:
            t = max(0.0, min(1.0, (
                (zone.position.x - a.x) * dx
                + (zone.position.y - a.y) * dy
            ) / length_sq))
            nearest_x, nearest_y = a.x + t * dx, a.y + t * dy
        radius_cells = zone.radius_ft / 5.0
        return (
            (nearest_x - zone.position.x) ** 2
            + (nearest_y - zone.position.y) ** 2
        ) <= radius_cells ** 2
    except Exception:
        logger.exception("Failed to test zone obstruction of sight line.")
        raise


def sight_line_is_obscured(
    observer: CombatantState,
    target: CombatantState,
    *,
    truesight_reaches: bool = False,
) -> bool:
    """Whether a live zone prevents this observer from seeing this target."""
    try:
        # The encounter is the source of truth; both state projections are
        # copies kept in sync so visibility callers need no setup argument.
        zones = observer.visible_obscuration_zones or target.visible_obscuration_zones
        for zone in zones:
            if zone.obscuration_kind == "none":
                continue
            if (
                zone.obscuration_kind == "magical-darkness"
                and truesight_reaches
            ):
                continue
            if _line_crosses_zone(observer, target, zone):
                return True
        return False
    except Exception:
        logger.exception("Unable to calculate source-neutral sight obscuration.")
        raise


def remove_concentration_obscuration_projections(
    states: list[CombatantState], source_id: str, effect_id: str,
) -> None:
    """Immediately remove source-owned zone projections on Concentration loss."""
    try:
        for state in states:
            state.visible_obscuration_zones = [
                zone for zone in state.visible_obscuration_zones
                if not (
                    zone.concentration and zone.source_id == source_id
                    and zone.action_id == effect_id
                )
            ]
            in_dark = any(
                zone.obscuration_kind == "magical-darkness"
                and state.position is not None
                and (zone.position.x - state.position.x) ** 2
                    + (zone.position.y - state.position.y) ** 2
                    <= (zone.radius_ft / 5) ** 2
                for zone in state.visible_obscuration_zones
            )
            if not in_dark:
                state.active_effect_ids = [
                    item for item in state.active_effect_ids
                    if item != "magical-darkness"
                ]
    except Exception:
        logger.exception("Failed to clear Concentration-owned obscuration.")
        raise
