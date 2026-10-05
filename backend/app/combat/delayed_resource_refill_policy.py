from __future__ import annotations

import logging

from app.combat.delayed_resource_refill_start import committed_refill_is_legal
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def has_printed_damaging_option(actor: EncounterCombatant) -> bool:
    """Return whether the creature still has a printed damaging attack or spell option."""
    try:
        template = actor.state.template
        if template.weapon_attack is not None or template.alternate_weapon_attacks:
            return True
        if template.attack_action is not None or template.area_weapon_attack_actions:
            return True
        if template.spell_attack_actions or template.auto_hit_spell_actions:
            return True
        if template.spell_save_actions or template.saving_throw_actions:
            return True
        return bool(template.hp_threshold_instant_death_actions)
    except Exception:
        logger.exception("Failed damaging-option probe for %s.", actor.combatant_id)
        raise RuntimeError("Damaging-option probe could not be resolved.") from None


def arena_may_start_committed_resource_refill(actor: EncounterCombatant) -> bool:
    """Arena starts a 1-minute rite only when no damaging option remains at all."""
    try:
        if has_printed_damaging_option(actor):
            return False
        return committed_refill_is_legal(actor)
    except Exception:
        logger.exception("Failed Arena committed-refill gate for %s.", actor.combatant_id)
        raise RuntimeError("Arena committed-refill gate could not be resolved.") from None
