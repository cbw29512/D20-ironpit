"""Source-owned defensive modifier consumption and early-ending lifecycle."""
import logging

from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.models import CombatantState
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


def consume_saving_throw_modifiers(state: CombatantState) -> list[str]:
    try:
        removed = [
            item.source_effect_id for item in state.active_modifiers
            if item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE and item.consume_on_saving_throw
        ]
        state.active_modifiers = [
            item for item in state.active_modifiers
            if not (item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE and item.consume_on_saving_throw)
        ]
        return sorted(set(removed))
    except Exception:
        logger.exception("Save modifier consumption failed for %s.", state.template.id)
        raise


def remove_owner_attack_ending_modifiers(state: CombatantState) -> list[str]:
    try:
        ending = [item for item in state.active_modifiers if item.ends_on_owner_attack]
        removed = [item.source_effect_id for item in ending]
        state.active_modifiers = [item for item in state.active_modifiers if not item.ends_on_owner_attack]
        ended_groups = {(item.source_id, item.source_effect_id) for item in ending}
        # If the protection is gone, its duration marker must leave the live card too.
        for effect in list(state.timed_effects):
            key = (effect.source_id, effect.source_effect_id)
            if key in ended_groups and not any(
                (item.source_id, item.source_effect_id) == key for item in state.active_modifiers
            ):
                remove_effect_group(state, effect)
        return sorted(set(removed))
    except Exception:
        logger.exception("Attack-ending modifier cleanup failed for %s.", state.template.id)
        raise
