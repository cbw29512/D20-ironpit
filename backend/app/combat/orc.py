from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.grapple import speed_is_zero
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.models import BattleEvent, CombatantState
from app.domain.traits import CombatTrait

ADRENALINE_RESOURCE_ID = "adrenaline-rush"
RELENTLESS_RESOURCE_ID = "relentless-endurance"


def _resource(state: CombatantState, resource_id: str):
    return next((item for item in state.resources if item.id == resource_id), None)


def proficiency_bonus(state: CombatantState) -> int:
    level = state.template.level
    if level is None:
        raise ValueError("Orc character traits require a character level.")
    return 2 + (level - 1) // 4


def adrenaline_rush_available(state: CombatantState) -> bool:
    resource = _resource(state, ADRENALINE_RESOURCE_ID)
    return (
        CombatTrait.ADRENALINE_RUSH in state.template.combat_traits
        and is_available(state, "bonus_action")
        and resource is not None
        and resource.current_uses > 0
    )


def use_adrenaline_rush(
    sequence: int,
    round_number: int,
    state: CombatantState,
    actor_id: str,
) -> BattleEvent | None:
    if not adrenaline_rush_available(state):
        return None
    resource = _resource(state, ADRENALINE_RESOURCE_ID)
    assert resource is not None
    resource.current_uses -= 1
    spend(state, "bonus_action")
    movement = 0 if speed_is_zero(state) else state.template.speed_ft
    state.movement_remaining_ft += movement
    grant_temporary_hit_points(state, proficiency_bonus(state))
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor_id,
        actor_name=state.template.name,
        feature_id=ADRENALINE_RESOURCE_ID,
        resource_remaining=resource.current_uses,
        movement_ft=movement,
        animation="dash",
        description=f"{state.template.name} uses Adrenaline Rush.",
    )


def use_relentless_endurance(state: CombatantState, remaining_damage: int) -> bool:
    if CombatTrait.RELENTLESS_ENDURANCE not in state.template.combat_traits:
        return False
    if remaining_damage >= state.template.max_hp:
        return False
    resource = _resource(state, RELENTLESS_RESOURCE_ID)
    if resource is None or resource.current_uses <= 0:
        return False
    resource.current_uses -= 1
    state.current_hp = 1
    state.is_alive = True
    state.is_unconscious = False
    state.is_stable = False
    return True
