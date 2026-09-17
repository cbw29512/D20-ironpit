from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.modifier_stack import effective_speed
from app.combat.offensive_ranges import offensive_ranges_for_target
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def needs_dash(member: EncounterCombatant, setup: EncounterSetup, turn_key: str) -> bool:
    """Use Dash only when normal movement cannot reach any certified offensive range."""
    if not member.state.template.progression_features.cunning_action:
        return False
    if not is_available(member.state, "bonus_action"):
        return False
    speed = effective_speed(member.state)
    if speed <= 0:
        return False
    normal_move = member.state.movement_remaining_ft
    dash_would_help = False
    for target in living_opponents(member, setup):
        distance = combatant_distance(member, target)
        for _, desired in offensive_ranges_for_target(member, target, turn_key):
            if distance <= desired + normal_move:
                return False
            if distance <= desired + normal_move + speed:
                dash_would_help = True
    return dash_would_help


def use_dash(
    sequence: int, round_number: int, member: EncounterCombatant, setup: EncounterSetup, turn_key: str,
) -> BattleEvent | None:
    """Spend Cunning Action on Dash only when it enables supported offense this turn."""
    if not needs_dash(member, setup, turn_key):
        return None
    spend(member.state, "bonus_action")
    member.state.movement_remaining_ft += effective_speed(member.state)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        feature_id="cunning-action-dash", animation="movement",
        description=f"{member.state.template.name} uses Cunning Action to Dash.",
    )
