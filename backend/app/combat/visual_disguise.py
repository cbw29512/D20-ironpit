"""Source-neutral encounter visual-disguise activation and first-turn dismissal."""
from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome, skill_check_bonus
from app.combat.condition_rules import can_see, has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def recognize_visual_disguise_by_physical_inspection(
    observer: CombatantState,
    source: CombatantState,
    source_id: str,
) -> bool:
    """Record observer-scoped recognition from qualifying tactile inspection."""
    try:
        rule = source.template.visual_disguise_action
        if (
            rule is None
            or not rule.physical_inspection_inconsistent
            or not source.magical_visual_disguise_active
            or source.is_dead
            or not source.is_alive
            or source.current_hp <= 0
        ):
            return False
        recognized = observer.recognized_visual_disguise_source_ids
        if source_id in recognized:
            return False
        recognized.append(source_id)
        return True
    except Exception as exc:
        logger.exception(
            "Physical visual-disguise inspection failed for source %s.", source_id
        )
        raise RuntimeError(
            "Physical visual-disguise inspection could not be resolved."
        ) from exc


def resolve_visual_disguise_opening(
    sequence: int, member: EncounterCombatant,
) -> BattleEvent:
    action = member.state.template.visual_disguise_action
    if action is None or not action.opening_eligible or not action.conceals_true_form:
        raise ValueError("No source-declared opening visual disguise available.")
    if member.state.opening_buff_id is not None or member.state.magical_visual_disguise_active:
        raise ValueError("Visual disguise cannot replace an existing opening buff.")
    if member.state.is_dead or member.state.current_hp <= 0:
        raise ValueError("A defeated combatant cannot disguise.")
    member.state.magical_visual_disguise_active = True
    member.state.opening_buff_id = action.id
    return BattleEvent(
        sequence=sequence, round_number=0, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        feature_id=action.id, animation="condition",
        description=f"Precombat preparation: {member.state.template.name} uses {action.name} as the free opening buff.",
    )


def resolve_visual_disguise_first_turn_dismissal(
    sequence: int, round_number: int, member: EncounterCombatant,
) -> BattleEvent | None:
    action = member.state.template.visual_disguise_action
    if (action is None or not action.dismiss_on_first_turn
            or not member.state.magical_visual_disguise_active
            or member.state.opening_buff_id != action.id
            or member.state.turns_started != 1):
        return None
    if not is_available(member.state, action.dismissal_cost):
        return None
    spend(member.state, action.dismissal_cost)
    member.state.magical_visual_disguise_active = False
    cost_label = "a Bonus Action" if action.dismissal_cost == "bonus_action" else "an Action"
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        feature_id=action.id, animation="condition-ended",
        description=(f"{member.state.template.name} dismisses {action.name} using {cost_label}; "
                     "its true form is now visible to eligible observers."),
    )


def resolve_visual_disguise_inspection(
    sequence: int, round_number: int, observer: EncounterCombatant,
    source: EncounterCombatant, dice, setup=None,
) -> BattleEvent:
    """Optional printed visual-inspection Action; not a free save or automatic AI turn.

    Recognizing that the subject is disguised is an observer-scoped fact;
    it NEVER removes a visual illusion, reveals the true form, or directly
    triggers any source's gaze condition. Source values come from the card.
    """
    if observer.combatant_id == source.combatant_id:
        raise ValueError("A visual disguise inspection requires a different creature.")
    rule = source.state.template.visual_disguise_action
    if rule is None or not source.state.magical_visual_disguise_active:
        raise ValueError("Target has no active source-declared visual disguise.")
    if source.state.is_dead or source.state.current_hp <= 0:
        raise ValueError("A dead source has no active visual disguise to inspect.")
    distance = combatant_distance(observer, source)
    if not can_see(observer.state, source.state, distance):
        raise ValueError("Inspecting a visual disguise requires sight of its owner.")
    if source.combatant_id in observer.state.recognized_visual_disguise_source_ids:
        raise ValueError("This observer already recognized that disguise.")
    if not is_available(observer.state, rule.inspection_cost):
        raise ValueError("Printed inspection action cost is unavailable.")
    ability = rule.inspection_ability
    skill = rule.inspection_skill
    disadvantage = ability_check_disadvantage_sources(observer.state, ability)
    disadvantage += int(
        has_condition(observer.state, "poisoned", setup=setup)
        or has_condition(observer.state, "frightened", setup=setup)
    )
    mode = ability_check_roll_mode(
        observer.state, disadvantage_sources=disadvantage,
        member=observer, setup=setup, skill=skill, relies_on_sight=True,
    )
    check = roll_d20(
        dice, skill_check_bonus(observer.state, ability, skill) + d20_modifier(observer.state),
        mode,
    )
    check, success = resolve_ability_check_outcome(
        observer.state, ability, check, rule.inspection_dc,
        dice=dice, round_number=round_number,
        encounter_roller=observer, setup=setup,
    )
    spend(observer.state, rule.inspection_cost)
    if success:
        observer.state.recognized_visual_disguise_source_ids.append(source.combatant_id)
    # The printed source only says "discern that the hag is disguised".
    # A successful check is not automatic sight of the original creature.
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=observer.combatant_id, actor_name=observer.state.template.name,
        target_id=source.combatant_id, target_name=source.state.template.name,
        feature_id=rule.id,
        ability_check_roll=check, check_ability=f"{ability} ({skill})",
        check_dc=rule.inspection_dc, check_succeeded=success,
        animation="condition",
        description=(
            f"{observer.state.template.name} spends {rule.inspection_cost.replace('_', ' ')} "
            f"to inspect {source.state.template.name}: "
            f"{'recognizes the disguise' if success else 'does not identify the disguise'} "
            f"({ability.title()} ({skill.title()}) DC {rule.inspection_dc})."
        ),
    )
