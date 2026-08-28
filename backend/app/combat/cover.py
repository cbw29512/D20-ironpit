from __future__ import annotations

import logging

from app.domain.models import BattlefieldState, CombatantState, CoverLevel

logger = logging.getLogger(__name__)
COVER_BONUS = {
    CoverLevel.NONE: 0,
    CoverLevel.HALF: 2,
    CoverLevel.THREE_QUARTERS: 5,
}


def _cover_level(
    target: CombatantState,
    battlefield: BattlefieldState | None,
) -> CoverLevel:
    try:
        if battlefield is None:
            return CoverLevel.NONE
        visibility = battlefield.visibility_by_actor.get(target.template.id)
        return CoverLevel.NONE if visibility is None else visibility.cover
    except Exception as exc:
        logger.exception("Cover state failed for %s.", target.template.name)
        raise RuntimeError("Cover state could not be resolved.") from exc


def resolve_attack_cover_bonus(
    target: CombatantState,
    battlefield: BattlefieldState | None,
) -> int:
    """Return AC cover bonus or reject direct targeting through Total Cover."""
    try:
        cover = _cover_level(target, battlefield)
        if cover is CoverLevel.TOTAL:
            raise ValueError("A target behind Total Cover cannot be targeted directly.")
        return COVER_BONUS[cover]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Attack cover failed for %s.", target.template.name)
        raise RuntimeError("Attack cover could not be resolved.") from exc


def resolve_dex_save_cover_bonus(
    target: CombatantState,
    battlefield: BattlefieldState | None,
) -> int:
    """Return the +2/+5 Dexterity-save bonus for partial cover."""
    try:
        cover = _cover_level(target, battlefield)
        return COVER_BONUS.get(cover, 0)
    except Exception as exc:
        logger.exception("Save cover failed for %s.", target.template.name)
        raise RuntimeError("Saving throw cover could not be resolved.") from exc
