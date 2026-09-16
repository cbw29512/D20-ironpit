from __future__ import annotations

import logging

from app.domain.models import CombatantState
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def sure_footed_advantage(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None,
) -> int:
    try:
        if CombatTrait.SURE_FOOTED not in state.template.combat_traits:
            return 0
        if ability not in {"strength", "dexterity"}:
            return 0
        return int(context is not None and context.condition_id == "prone")
    except Exception:
        logger.exception("Failed to resolve Sure-Footed saving throw Advantage for %s.", state.template.name)
        raise
