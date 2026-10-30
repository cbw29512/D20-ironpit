from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import EncounterCombatant, EncounterSetup, SavingThrowAction
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _forbidden_effect_families(action: SavingThrowAction) -> set[str]:
    return {
        effect.effect_family for effect in action.failure_effects
        if getattr(effect, "effect_family", None)
    }


def save_action_target_eligible(
    action: SavingThrowAction,
    target: EncounterCombatant,
    actor: EncounterCombatant | None = None,
    setup: EncounterSetup | None = None,
) -> bool:
    """Return whether target-state restrictions permit this save action, ignoring range."""
    try:
        if action.required_target_condition and not has_condition(target.state, action.required_target_condition):
            return False
        if action.required_target_grappled_by_self:
            if actor is None or not any(
                source.source_id == actor.combatant_id
                for source in target.state.grapple_sources
            ):
                return False
        if action.max_active_grapple_targets is not None:
            if actor is None or setup is None:
                return False
            members = [*setup.heroes, *setup.monsters]
            active_targets = [
                member
                for member in members
                if any(
                    source.source_id == actor.combatant_id
                    and source.source_effect_id == action.id
                    for source in member.state.grapple_sources
                )
            ]
            target_already_active = any(
                member.combatant_id == target.combatant_id for member in active_targets
            )
            if (
                not target_already_active
                and len(active_targets) >= action.max_active_grapple_targets
            ):
                return False
        if action.forbid_target_affected_by_action:
            families = _forbidden_effect_families(action)
            if families and any(
                effect.effect_family in families for effect in target.state.timed_effects
            ):
                return False
            if not families and any(
                effect.source_effect_id == action.id for effect in target.state.timed_effects
            ):
                return False
        return action.target_max_size is None or size_at_most(
            target.state.template.size,
            action.target_max_size,
        )
    except Exception:
        logger.exception("Failed save-action target eligibility check for %s.", action.id)
        raise


def legal_save_action(
    action: SavingThrowAction,
    target: EncounterCombatant,
    distance_ft: int,
    actor: EncounterCombatant | None = None,
    setup: EncounterSetup | None = None,
) -> bool:
    """Resolve reusable save-action target restrictions, including grapple ownership."""
    try:
        if distance_ft > action.range_ft:
            return False
        return save_action_target_eligible(action, target, actor, setup)
    except Exception:
        logger.exception("Failed save-action legality check for %s.", action.id)
        raise


__all__ = ["legal_save_action", "save_action_target_eligible"]
