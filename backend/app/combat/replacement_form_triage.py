"""Source-neutral AI choice between emergency form and self-healing."""
from __future__ import annotations

import logging
from app.combat.action_economy import is_available
from app.combat.healing_policy import healing_dice_maximized
from app.combat.resource_conversion import restoration_conversion
from app.combat.resources import resource_available
from app.content.replacement_form_registry import replacement_form_source_template

logger = logging.getLogger(__name__)


def emergency_form_buffer(state, form, owner) -> float:
    """New absorbable HP: Beast pool in 2014 or net Temporary HP in 2024."""
    try:
        if form.hp_mode == "form_pool":
            return float(replacement_form_source_template(
                owner.ruleset, form.form_template_id,
            ).max_hp)
        if form.hp_mode == "retain_owner":
            return float(max(0, form.temporary_hp_on_enter - state.temporary_hp))
        raise ValueError(f"Unsupported form HP mode {form.hp_mode!r}.")
    except Exception:
        logger.exception("Cannot score emergency form buffer %s.", form.id)
        raise


def defer_self_healing_for_form(healer, healing, turn_key) -> bool:
    """Preserve healing except when a legal same-cost emergency form wins."""
    try:
        state = healer.state
        owner = state.replacement_form.original_template if state.replacement_form else state.template
        form = next((a for a in owner.replacement_form_actions if a.ai_use_policy == "emergency_only"), None)
        if form is None or state.replacement_form is not None:
            return False
        if not (0 < state.current_hp <= owner.max_hp * form.ai_emergency_hp_fraction):
            return False
        if healing.action_cost != form.action_cost or healing.max_targets != 1:
            return False
        if (healing.stabilize_at_zero or healing.healing_from_resource_pool
            or healing.shared_healing_pool is not None
            or healing.percentile_success_max is not None
            or healing.removable_conditions or healing.prone_reaction_stand):
            return False
        if not is_available(state, form.action_cost):
            return False
        if not resource_available(state, form.resource_id, form.resource_cost):
            if restoration_conversion(state, form.resource_id, turn_key) is None:
                return False
        buffer = emergency_form_buffer(state, form, owner)
        if buffer <= 0:
            return False
        expected = healing.healing_bonus + healing.dice_count * (
            healing.dice_size if healing_dice_maximized(healer, healer)
            else (healing.dice_size + 1) / 2
        )
        if healing.restore_to_effective_max:
            expected = owner.max_hp - state.current_hp
        elif healing.grants_temporary_hp:
            expected = max(0, expected - state.temporary_hp)
        else:
            expected = min(max(0, owner.max_hp - state.current_hp), expected)
        return buffer > expected
    except Exception:
        logger.exception("Emergency form/self-healing selection failed for %s.", healer.combatant_id)
        raise
