"""AI-only forecast of severe failed-save conditions that a form *actually* mitigates.

This is deliberately narrow: a single currently reachable target, source-declared
single-target saving-throw Actions/spells, and existing source condition defenses.
No imaginary condition-to-damage conversion or RAW mutation.
"""
from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import can_see, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.spell_policy import spell_at_slot, spell_has_higher_slot_scaling
from app.combat.spell_policy_targeting import area_spell_choice, legacy_radius_spell_choice
from app.combat.offense_value import _save_success_probability
from app.combat.resources import resource_available
from app.combat.saving_throws import legal_save_action
from app.combat.spell_policy_targeting import legal_single_spell_targets
from app.combat.spellcasting import legal_slot_levels
from app.combat.temporary_terrain import spell_terrain_is_supported
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template

logger = logging.getLogger(__name__)

SEVERE_CONDITIONS = frozenset({
    "incapacitated", "paralyzed", "petrified", "stunned", "unconscious",
})
# Tactical guardrail. These are probabilities, not converted HP/damage values.
MIN_FAILURE_RISK = 0.50
MIN_FORM_IMPROVEMENT = 0.25


def failure_chance(target, action) -> float:
    return max(0.0, min(1.0, 1.0 - _save_success_probability(target, action)))


def form_mitigates_disabling_save(member, setup, form) -> bool:
    """True only if a *legal* severe save is significantly safer in the form."""
    try:
        if form.ai_use_policy != "emergency_only":
            return False
        opponents = setup.monsters if member.side == "heroes" else setup.heroes
        sources = [enemy for enemy in opponents if (
            enemy.state.is_alive and not enemy.state.is_dead
            and enemy.state.current_hp > 0 and not is_incapacitated(enemy.state)
        )]
        # Single-target focus is predictable only if this is the sole live
        # opponent. AOE choices may target multiple opponents using *actual*
        # area placement rules, not hypothetical focus fire.
        allies = setup.heroes if member.side == "heroes" else setup.monsters
        solo = len([ally for ally in allies if ally.state.is_alive and not ally.state.is_dead
                    and ally.state.current_hp > 0]) == 1
        if not sources:
            return False
        members = {row.combatant_id: row for row in [*setup.heroes, *setup.monsters]}
        owner = member.state.replacement_form.original_template if member.state.replacement_form else member.state.template
        source = replacement_form_source_template(owner.ruleset, form.form_template_id)
        compiled = compile_replacement_form_template(
            owner, source,
            retain_spellcasting=form.retain_spellcasting,
            retained_spell_action_ids=form.retained_spell_action_ids,
            retain_creature_type=form.retain_creature_type,
            retain_hit_points=form.hp_mode == "retain_owner",
        )
        shaped = member.model_copy(update={
            "state": member.state.model_copy(update={"template": compiled}),
        })
        for enemy in sources:
            distance = combatant_distance(enemy, member)
            actions = []
            for action in enemy.state.template.saving_throw_actions:
                if (not solo or action.action_cost == "reaction" or action.max_targets != 1
                    or action.area is not None or distance > action.range_ft
                    or not resource_available(enemy.state, action.resource_id, action.resource_cost)
                    or not legal_save_action(action, member, distance, source_id=enemy.combatant_id)
                    or (action.requires_target_sight and not can_see(enemy.state, member.state, distance))):
                    continue
                actions.append((action, action.magical_effect))
            for action in enemy.state.template.spell_save_actions:
                area = action.area is not None or action.area_radius_ft is not None
                if (action.action_cost == "reaction" or action.cast_rounds != 1 or action.repeat_only
                    or (action.concentration and enemy.state.concentration is not None)
                    or not spell_terrain_is_supported(action)
                    or (not area and (
                        not solo or action.target_count != 1 or action.target_count_per_slot_above != 0
                    ))):
                    continue
                slots = legal_slot_levels(
                    enemy.state, f"forecast:{enemy.combatant_id}", action.level,
                    higher_slot_scaling=spell_has_higher_slot_scaling(action),
                )
                if not slots:
                    continue
                if not area:
                    if member in legal_single_spell_targets(enemy, setup, action):
                        actions.append((action, True))
                    continue
                # The same ally-safe placement actually chosen by spell
                # resolution. An arbitrary reachable blast is not a forecast.
                for slot in slots:
                    scaled = spell_at_slot(action, slot)
                    if action.area is not None:
                        choice = area_spell_choice(enemy, setup, action, slot, scaled, members)
                    else:
                        choice = legacy_radius_spell_choice(
                            enemy, setup, action, slot, scaled, members, None,
                        )
                    if (choice is not None and choice.placement is not None
                        and member.combatant_id in choice.placement.enemy_ids):
                        actions.append((action, True))
                        break
            for action, magical in actions:
                rider = action.failed_save_timed_effect
                condition = rider.effect_id if rider is not None else None
                if condition not in SEVERE_CONDITIONS:
                    continue
                if condition_is_immune(
                    member.state, condition, enemy.state.template, source_is_magical=magical,
                ):
                    continue
                exposed = failure_chance(member, action)
                if exposed < MIN_FAILURE_RISK:
                    continue
                protected = 0.0 if condition_is_immune(
                    shaped.state, condition, enemy.state.template, source_is_magical=magical,
                ) else failure_chance(shaped, action)
                if exposed - protected >= MIN_FORM_IMPROVEMENT:
                    return True
        return False
    except Exception:
        logger.exception("Failed form protection vs disabling save for %s.", member.combatant_id)
        raise
