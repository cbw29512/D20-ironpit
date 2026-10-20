"""Source-neutral encounter visual-disguise activation and first-turn dismissal."""
from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent


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
