from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import EncounterCombatant, SavingThrowAction
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _forbidden_effect_families(action: SavingThrowAction) -> set[str]:
    return {
        effect.effect_family for effect in action.failure_effects
        if getattr(effect, "effect_family", None)
    }


def legal_save_action(
    action: SavingThrowAction,
    target: EncounterCombatant,
    distance_ft: int,
    actor: EncounterCombatant | None = None,
) -> bool:
    """Resolve reusable save-action target restrictions, including grapple ownership."""
    try:
        if distance_ft > action.range_ft:
            return False
        if action.required_target_condition and not has_condition(target.state, action.required_target_condition):
            return False
        if action.required_target_grappled_by_self:
            if actor is None or not any(source.source_id == actor.combatant_id for source in target.state.grapple_sources):
                return False
        if action.forbid_target_affected_by_action:
            families = _forbidden_effect_families(action)
            if families and any(effect.effect_family in families for effect in target.state.timed_effects):
                return False
            if not families and any(effect.source_effect_id == action.id for effect in target.state.timed_effects):
                return False
        return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)
    except Exception:
        logger.exception("Failed save-action legality check for %s.", action.id)
        raise


__all__ = ["legal_save_action"]
