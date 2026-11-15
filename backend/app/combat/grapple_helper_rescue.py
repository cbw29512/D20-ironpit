"""Reusable allied rescue check against a source-owned Grapple rule.

Definition is owned by the grappling source. Fight state links that source
to the held target; helper spends its own Action for a universal ability check.
"""
from __future__ import annotations

import logging

from app.combat.ability_check_escape import ability_check_bonus
from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import has_condition, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.grapple import release_grapple
from app.combat.grapple_appendage_capacity import record_broken_grapple_appendage
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grapple_rescue import GrappleRescueRule
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def eligible(
    helper: EncounterCombatant,
    target: EncounterCombatant,
    owner: EncounterCombatant,
    rule: GrappleRescueRule,
) -> bool:
    try:
        return (
            (rule.allow_held_target or helper.combatant_id != target.combatant_id)
            and helper.side == target.side != owner.side
            and helper.state.is_alive and not helper.state.is_dead
            and target.state.is_alive and not target.state.is_dead
            and owner.state.is_alive and not owner.state.is_dead
            and not is_incapacitated(helper.state)
            and is_available(helper.state, rule.action_cost)
            and helper.state.template.ability_scores is not None
            and combatant_distance(
                helper, target if rule.helper_range_anchor == "held_target" else owner,
            ) <= rule.helper_range_ft
            and rule in owner.state.template.grapple_rescue_rules
            and any(
                g.source_id == owner.combatant_id
                and g.linked_effect_id == rule.source_action_id
                and (not rule.requires_breakable_object or g.breakable_object is not None)
                for g in target.state.grapple_sources
            )
        )
    except Exception:
        logger.exception("Failed source-linked Grapple rescue eligibility.")
        raise


def choose_grapple_helper_rescue(
    helper: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[EncounterCombatant, EncounterCombatant, GrappleRescueRule] | None:
    try:
        allies = setup.heroes if helper.side == "heroes" else setup.monsters
        opponents = setup.monsters if helper.side == "heroes" else setup.heroes
        choices = [
            (owner, target, rule)
            for owner in opponents for rule in owner.state.template.grapple_rescue_rules
            for target in allies
            if eligible(helper, target, owner, rule)
        ]
        return min(
            choices,
            key=lambda item: (item[1].state.current_hp, item[1].combatant_id, item[0].combatant_id),
            default=None,
        )
    except Exception:
        logger.exception("Failed Grapple helper choice for %s.", helper.combatant_id)
        raise


def resolve_grapple_helper_rescue(
    sequence: int,
    round_number: int,
    helper: EncounterCombatant,
    target: EncounterCombatant,
    owner: EncounterCombatant,
    rule: GrappleRescueRule,
    dice,
    setup: EncounterSetup,
) -> BattleEvent:
    try:
        if not eligible(helper, target, owner, rule):
            raise ValueError("Helper rescue target, owner, or Action is not legal.")
        ability = rule.check_ability
        disadvantage = ability_check_disadvantage_sources(helper.state, ability)
        disadvantage += int(
            has_condition(helper.state, "poisoned")
            or has_condition(helper.state, "frightened", setup=setup)
        )
        mode = ability_check_roll_mode(
            helper.state, ability=ability, disadvantage_sources=disadvantage,
            member=helper, setup=setup,
        )
        check = roll_d20(dice, ability_check_bonus(helper.state, ability) + d20_modifier(helper.state), mode)
        check, succeeded = resolve_ability_check_outcome(
            helper.state, ability, check, rule.check_dc,
            dice=dice, round_number=round_number,
            encounter_roller=helper, setup=setup,
        )
        spend(helper.state, rule.action_cost)
        before_conditions = set(target.state.active_effect_ids)
        if succeeded:
            if rule.requires_breakable_object:
                record_broken_grapple_appendage(
                    setup, owner.combatant_id, rule.source_action_id,
                )
            release_grapple(target.state, owner.combatant_id)
        removed = sorted(before_conditions - set(target.state.active_effect_ids))
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=helper.combatant_id, actor_name=helper.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=rule.source_action_id, animation="escape-check",
            ability_check_roll=check, check_ability=ability, check_dc=rule.check_dc,
            check_succeeded=succeeded,
            removed_condition_ids=removed,
            description=(
                f"{helper.state.template.name} uses an Action to "
                f"{rule.release_verb} {owner.state.template.name}'s "
                f"{rule.source_name} holding {target.state.template.name}; "
                f"{ability.title()} DC {rule.check_dc} "
                f"{'succeeds' if succeeded else 'fails'}."
            ),
        )
    except Exception:
        logger.exception("Failed Grapple helper rescue for %s.", helper.combatant_id)
        raise
