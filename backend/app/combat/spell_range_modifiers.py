from __future__ import annotations

import logging

from app.combat.resources import resource_available, spend_resource
from app.domain.runtime import CombatantState
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier

logger = logging.getLogger(__name__)


def choose_spell_range_modifier(
    state: CombatantState,
    *,
    base_range_ft: int,
    required_range_ft: int,
) -> ResourceBackedSpellRangeModifier | None:
    """Choose a legal range modifier only when normal spell range is insufficient."""
    try:
        if required_range_ft <= base_range_ft:
            return None
        legal = [
            option
            for option in state.template.spell_range_modifiers
            if base_range_ft >= option.minimum_base_range_ft
            and required_range_ft <= base_range_ft * option.range_multiplier
            and resource_available(state, option.resource_id, option.resource_cost)
        ]
        return max(legal, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Failed to choose spell range modifier for %s.", state.template.name)
        raise RuntimeError("Spell range modifier could not be selected.") from exc


def effective_spell_range_ft(state: CombatantState, base_range_ft: int) -> int:
    """Return the farthest currently legal range without spending a resource yet."""
    try:
        ranges = [base_range_ft]
        for option in state.template.spell_range_modifiers:
            if (
                base_range_ft >= option.minimum_base_range_ft
                and resource_available(state, option.resource_id, option.resource_cost)
            ):
                ranges.append(base_range_ft * option.range_multiplier)
        return max(ranges)
    except Exception as exc:
        logger.exception("Failed to compute effective spell range for %s.", state.template.name)
        raise RuntimeError("Effective spell range could not be computed.") from exc


def spend_spell_range_modifier(
    state: CombatantState,
    option: ResourceBackedSpellRangeModifier | None,
) -> int | None:
    """Spend the range-modifier resource after a cast using extended range is committed."""
    try:
        if option is None:
            return None
        return spend_resource(state, option.resource_id, option.resource_cost)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to spend spell range modifier for %s.", state.template.name)
        raise RuntimeError("Spell range modifier resource could not be spent.") from exc
