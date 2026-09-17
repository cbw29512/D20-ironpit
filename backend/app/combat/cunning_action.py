from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.modifier_stack import effective_speed
from app.combat.offensive_ranges import offensive_ranges_for_target
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def needs_dash(member: EncounterCombatant, setup: EncounterSetup, turn_key: str) -> bool:
    if not member.state.template.progression_features.cunning_action:
        return False
    if not is_available(member.state, "bonus_action") or member.state.movement_remaining_ft <= 0:
        return False
    for target in living_opponents(member, setup):
        distance = combatant_distance(member, target)
        if any(distance <= desired for _, desired in offensive_ranges_for_target(member, target, turn_key)):
            return False
    return True


def use_dash(
    sequence: int, round_number: int, member: EncounterCombatant, setup: EncounterSetup, turn_key: str,
) -> BattleEvent | None:
    """Spend Cunning Action on Dash only when ordinary movement has no legal offense already."""
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
