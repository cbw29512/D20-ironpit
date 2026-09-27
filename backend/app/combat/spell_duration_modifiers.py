from __future__ import annotations

import logging

from app.combat.resources import resource_available, spend_resource
from app.domain.runtime import CombatantState
from app.domain.spell_cast_modifiers import ResourceBackedSpellDurationModifier

logger = logging.getLogger(__name__)


def choose_spell_duration_modifier(
    state: CombatantState,
    *,
    base_duration_minutes: int,
) -> ResourceBackedSpellDurationModifier | None:
    """Choose the highest-priority legal duration modifier for a qualifying spell."""
    try:
        legal = [
            option for option in state.template.spell_duration_modifiers
            if base_duration_minutes >= option.minimum_base_duration_minutes
            and resource_available(state, option.resource_id, option.resource_cost)
        ]
        return max(legal, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Failed to choose spell duration modifier for %s.", state.template.name)
        raise RuntimeError("Spell duration modifier could not be selected.") from exc


def effective_spell_duration_minutes(
    base_duration_minutes: int,
    option: ResourceBackedSpellDurationModifier | None,
) -> int:
    if option is None:
        return base_duration_minutes
    return min(
        base_duration_minutes * option.duration_multiplier,
        option.maximum_duration_minutes,
    )


def spend_spell_duration_modifier(
    state: CombatantState,
    option: ResourceBackedSpellDurationModifier | None,
) -> int | None:
    """Spend the duration-modifier resource only once the modified cast is committed."""
    try:
        if option is None:
            return None
        return spend_resource(state, option.resource_id, option.resource_cost)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to spend spell duration modifier for %s.", state.template.name)
        raise RuntimeError("Spell duration modifier resource could not be spent.") from exc
