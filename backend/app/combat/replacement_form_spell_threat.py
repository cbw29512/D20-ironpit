"""Legal, target-specific spell-damage preview for universal survival AI.

Read-only hypothetical fresh Action economy. Reuses the actual offensive spell
choosers; scores only harm to this defender, not whole-party spell damage.
"""
from __future__ import annotations

import logging

from app.combat.auto_hit_spell_policy import choose_auto_hit_spell
from app.combat.concentration_repeat_saves import choose_concentration_repeat_save
from app.combat.condition_rules import is_incapacitated
from app.combat.offense_value import save_spell_expected_damage
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_policy import choose_spell, spell_at_slot

logger = logging.getLogger(__name__)


def single_enemy_spell_pressure(enemy, defender, setup) -> float:
    """Expected incoming spell damage from one plausible legal chosen spell."""
    try:
        state = enemy.state
        if (state.is_dead or not state.is_alive or state.current_hp <= 0
            or is_incapacitated(state)):
            return 0.0
        template = state.template
        if not (template.auto_hit_spell_actions or template.spell_attack_actions
                or template.spell_save_actions or template.concentration_repeat_save_actions):
            return 0.0

        # Preview the opponent's *next* turn without mutating fight state.
        # Keep remaining slots, concentration, conditions and geometry intact.
        future_state = state.model_copy(update={
            "action_available": True,
            "bonus_action_available": True,
            "turn_terminated": False,
            "voluntary_turn_activity": None,
        })
        candidate = enemy.model_copy(update={"state": future_state})
        turn_key = f"forecast:{enemy.combatant_id}"
        scores = []
        if template.auto_hit_spell_actions:
            auto = choose_auto_hit_spell(candidate, setup, turn_key)
            if auto is not None and auto.target.combatant_id == defender.combatant_id:
                scores.append(auto.expected_damage)
        if template.spell_attack_actions:
            attack = choose_spell_attack(candidate, setup, turn_key)
            if attack is not None and attack.target.combatant_id == defender.combatant_id:
                scores.append(attack.expected_damage)
        if template.spell_save_actions:
            save = choose_spell(candidate, setup, turn_key)
            if save is not None and defender.combatant_id in save.target_ids:
                scores.append(save_spell_expected_damage(
                    defender, spell_at_slot(save.action, save.slot_level),
                ))
        if future_state.concentration is not None and template.concentration_repeat_save_actions:
            repeat = choose_concentration_repeat_save(candidate, setup)
            if repeat is not None and defender.combatant_id in repeat.spell_choice.target_ids:
                choice = repeat.spell_choice
                scores.append(save_spell_expected_damage(
                    defender, spell_at_slot(choice.action, choice.slot_level),
                ))
        return max([0.0, *scores])
    except Exception:
        logger.exception("Incoming spell pressure failed for %s.", enemy.combatant_id)
        raise
