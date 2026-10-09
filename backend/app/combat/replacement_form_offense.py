"""Source-neutral AI opportunity comparison: fresh form versus legal spell offense.

The printed form and spell rules never change; this only guides a caster AI.
"""
from __future__ import annotations

import logging

from app.combat.auto_hit_spell_policy import choose_auto_hit_spell
from app.combat.concentration_repeat_saves import choose_concentration_repeat_save
from app.combat.replacement_form_triage import emergency_form_buffer
from app.combat.replacement_form_threat import incoming_attack_pressure, pressure_may_be_lethal
from app.combat.replacement_form_condition_threat import form_mitigates_disabling_save
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_policy import choose_spell

logger = logging.getLogger(__name__)


def favor_spell_over_emergency_form(
    hp: float, max_hp: float, emergency_fraction: float,
    form_buffer: float, spell_damage: float,
) -> bool:
    """Severe danger favors survival; otherwise compare known useful values."""
    if hp <= 0 or max_hp <= 0 or form_buffer <= 0 or spell_damage <= 0:
        return False
    if hp <= max_hp * emergency_fraction / 2:
        return False  # Very near death: preserve the survival buffer.
    return spell_damage >= form_buffer


def defer_emergency_form_for_spell(member, setup, form, turn_key: str) -> bool:
    """Use existing legal spell choosers; never guess spell damage by name."""
    try:
        if form.ai_use_policy != "emergency_only":
            return False
        state = member.state
        owner = state.replacement_form.original_template if state.replacement_form else state.template
        if not (0 < state.current_hp <= owner.max_hp * form.ai_emergency_hp_fraction):
            return False
        buffer = emergency_form_buffer(state, form, owner)
        if buffer <= 0:
            return False
        if form_mitigates_disabling_save(member, setup, form):
            return False  # Preserve a real reduction in severe failed-save danger.
        pressure = incoming_attack_pressure(member, setup)
        if pressure_may_be_lethal(state.current_hp, state.temporary_hp, pressure):
            return False  # A plausible lethal Action beats speculative damage.
        options = (
            choose_auto_hit_spell(member, setup, turn_key),
            choose_spell_attack(member, setup, turn_key),
            choose_spell(member, setup, turn_key),
            choose_concentration_repeat_save(member, setup),
        )
        for choice in options:
            if choice is None:
                continue
            candidate = getattr(choice, "spell_choice", choice)
            spell_action = choice.action
            same_cost = spell_action.action_cost == form.action_cost
            blocks_casting = (
                form.action_cost == "bonus_action"
                and spell_action.action_cost == "action"
                and spell_action.id not in form.retained_spell_action_ids
            )
            if not (same_cost or blocks_casting):
                continue
            if favor_spell_over_emergency_form(
                state.current_hp, owner.max_hp, form.ai_emergency_hp_fraction,
                buffer, candidate.expected_damage,
            ):
                return True
        return False
    except Exception:
        logger.exception("Replacement-form spell opportunity failed for %s.", member.combatant_id)
        raise
