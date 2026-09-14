from __future__ import annotations

from app.domain.models import CombatantState
from app.domain.traits import CombatTrait

LIMITED_MAGIC_IMMUNITY_MAX_LEVEL = 6


def spell_affects_target(state: CombatantState, cast_level: int) -> bool:
    """Return whether a spell casting can affect this target under universal immunity traits."""
    return not (
        CombatTrait.LIMITED_MAGIC_IMMUNITY in state.template.combat_traits
        and cast_level <= LIMITED_MAGIC_IMMUNITY_MAX_LEVEL
    )
