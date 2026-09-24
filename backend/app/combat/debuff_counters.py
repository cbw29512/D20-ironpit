from __future__ import annotations

import logging

from app.domain.debuffs import DebuffCounter, DebuffCounterMode
from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def _scope_matches(counter: DebuffCounter, source_is_magical: bool) -> bool:
    if counter.source_scope == "any":
        return True
    if counter.source_scope == "magical":
        return source_is_magical
    return not source_is_magical


def matching_debuff_counters(
    state: CombatantState,
    debuff_id: str,
    *,
    source_is_magical: bool = False,
    mode: DebuffCounterMode | None = None,
) -> list[DebuffCounter]:
    """Return active buff-owned counters that match one debuff application/state."""
    try:
        owned = [
            counter
            for effect in state.timed_effects
            for counter in effect.owned_debuff_counters
        ]
        owned.extend(
            item.debuff_counter
            for item in state.active_modifiers
            if item.kind is ModifierKind.DEBUFF_COUNTER and item.debuff_counter is not None
        )
        return [
            counter
            for counter in owned
            if counter.debuff_id == debuff_id
            and _scope_matches(counter, source_is_magical)
            and (mode is None or counter.mode == mode)
        ]
    except Exception:
        logger.exception("Failed to resolve debuff counters for %s / %s.", state.template.name, debuff_id)
        raise


def debuff_is_countered(
    state: CombatantState,
    debuff_id: str,
    *,
    source_is_magical: bool = False,
) -> bool:
    """Return whether an active buff prevents this debuff from applying/operating."""
    return bool(matching_debuff_counters(
        state,
        debuff_id,
        source_is_magical=source_is_magical,
        mode="prevent",
    ))


def movement_counter_cost(
    state: CombatantState,
    debuff_id: str,
    *,
    source_is_magical: bool = False,
) -> int | None:
    """Return the cheapest active movement cost that can clear this debuff."""
    counters = matching_debuff_counters(
        state,
        debuff_id,
        source_is_magical=source_is_magical,
        mode="remove-with-movement",
    )
    return min((item.movement_cost_ft for item in counters), default=None)


def difficult_terrain_multiplier(
    state: CombatantState,
    *,
    source_is_magical: bool = False,
) -> int:
    """Return the ordinary 2x difficult-terrain cost unless a buff counters it."""
    return 1 if debuff_is_countered(
        state,
        "difficult-terrain",
        source_is_magical=source_is_magical,
    ) else 2
