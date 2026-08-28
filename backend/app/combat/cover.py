from __future__ import annotations

import logging

from app.domain.models import BattlefieldState, CombatantState, CoverLevel

logger = logging.getLogger(__name__)
COVER_AC_BONUS = {
    CoverLevel.NONE: 0,
    CoverLevel.HALF: 2,
    CoverLevel.THREE_QUARTERS: 5,
}


def resolve_attack_cover_bonus(
    target: CombatantState,
    battlefield: BattlefieldState | None,
) -> int:
    """Return the target's cover AC bonus or reject direct targeting through Total Cover."""
    try:
        if battlefield is None:
            return 0
        visibility = battlefield.visibility_by_actor.get(target.template.id)
        cover = CoverLevel.NONE if visibility is None else visibility.cover
        if cover is CoverLevel.TOTAL:
            raise ValueError("A target behind Total Cover cannot be targeted directly.")
        return COVER_AC_BONUS[cover]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Cover resolution failed for %s.", target.template.name)
        raise RuntimeError("Cover could not be resolved.") from exc
