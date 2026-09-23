from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def can_see(observer: CombatantState, subject: CombatantState) -> bool:
    """Resolve ordinary sight from universal combat conditions.

    Special senses are intentionally not invented here; they can extend this
    primitive when their source data is certified.
    """
    try:
        return not has_condition(observer, "blinded") and not has_condition(subject, "invisible")
    except Exception as exc:
        logger.exception("Combat sight resolution failed.")
        raise RuntimeError("Combat sight could not be resolved.") from exc


def can_hear(observer: CombatantState, _subject: CombatantState) -> bool:
    try:
        return not has_condition(observer, "deafened")
    except Exception as exc:
        logger.exception("Combat hearing resolution failed.")
        raise RuntimeError("Combat hearing could not be resolved.") from exc


def can_see_or_hear(observer: CombatantState, subject: CombatantState) -> bool:
    try:
        return can_see(observer, subject) or can_hear(observer, subject)
    except Exception as exc:
        logger.exception("Combat perception resolution failed.")
        raise RuntimeError("Combat perception could not be resolved.") from exc
