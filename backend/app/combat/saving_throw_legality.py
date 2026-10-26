from __future__ import annotations

import logging

from app.combat.condition_rules import can_see, has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.source_effect_immunity import (
    has_shared_source_effect_immunity,
    has_source_effect_immunity,
)
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant
from app.domain.models import SavingThrowAction
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def legal_save_action(
    action: SavingThrowAction,
    target: EncounterCombatant,
    distance_ft: int,
    source_id: str | None = None,
    actor: EncounterCombatant | None = None,
) -> bool:
    try:
        template = target.state.template
        if source_id and has_source_effect_immunity(target.state, action.id, source_id):
            return False
        if (
            action.source_effect_immunity_keys_blocking
            and has_shared_source_effect_immunity(
                target.state, action.source_effect_immunity_keys_blocking
            )
        ):
            return False
        if (
            action.required_target_condition is not None
            and not has_condition(target.state, action.required_target_condition)
        ):
            return False
        if action.prohibited_target_source_effect_ids and any(
            effect.source_effect_id in action.prohibited_target_source_effect_ids
            for effect in target.state.timed_effects
        ):
            return False
        if (
            actor is not None
            and action.requires_target_sight
            and not can_see(
                actor.state, target.state, combatant_distance(actor, target)
            )
        ):
            return False
        if action.requires_target_to_see_source and (
            actor is None
            or not can_see(
                target.state, actor.state, combatant_distance(actor, target)
            )
        ):
            return False
        if distance_ft > action.range_ft:
            return False
        if (
            action.requires_target_hearing
            and "deafened" in target.state.active_effect_ids
        ):
            return False
        if action.required_target_creature_types and not any(
            is_creature_type(template, kind)
            for kind in action.required_target_creature_types
        ):
            return False
        if any(
            is_creature_type(template, kind)
            for kind in action.excluded_target_creature_types
        ):
            return False
        return (
            action.target_max_size is None
            or size_at_most(template.size, action.target_max_size)
        )
    except Exception:
        logger.exception(
            "Failed to evaluate save-action legality for %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
