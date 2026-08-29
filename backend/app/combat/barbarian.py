from __future__ import annotations

from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack

RAGE_EFFECT_ID = "rage"
_RAGE_RESISTANCES = (
    DamageType.BLUDGEONING,
    DamageType.PIERCING,
    DamageType.SLASHING,
)


def _rage_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == "rage"), None)


def rage_active(state: CombatantState) -> bool:
    return RAGE_EFFECT_ID in state.active_effect_ids


def rage_damage_bonus(state: CombatantState, attack: WeaponAttack) -> int:
    if not rage_active(state) or not attack.rage_eligible:
        return 0
    return state.template.rage_damage_bonus


def enter_rage(
    sequence: int,
    round_number: int,
    state: CombatantState,
    actor_id: str,
) -> BattleEvent | None:
    """Use a Bonus Action and one Rage use, then apply the 2024 Rage combat effects."""
    if state.template.rage_damage_bonus <= 0 or rage_active(state):
        return None
    resource = _rage_resource(state)
    if resource is None or resource.current_uses <= 0 or not state.bonus_action_available:
        return None

    resource.current_uses -= 1
    state.bonus_action_available = False
    state.active_effect_ids.append(RAGE_EFFECT_ID)
    for damage_type in _RAGE_RESISTANCES:
        if damage_type not in state.temporary_damage_resistances:
            state.temporary_damage_resistances.append(damage_type)
    state.rage_expires_round = round_number + 1
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor_id,
        actor_name=state.template.name,
        feature_id=RAGE_EFFECT_ID,
        resource_remaining=resource.current_uses,
        animation="rage",
        description=f"{state.template.name} enters Rage.",
    )


def extend_rage_from_attack(state: CombatantState, round_number: int) -> None:
    """Making an attack roll extends Rage through the end of the Barbarian's next turn."""
    if rage_active(state):
        state.rage_expires_round = round_number + 1


def maintain_rage_with_bonus_action(
    sequence: int,
    round_number: int,
    state: CombatantState,
    actor_id: str,
) -> BattleEvent | None:
    if not rage_active(state) or state.rage_expires_round is None:
        return None
    if state.rage_expires_round > round_number or not state.bonus_action_available:
        return None
    state.bonus_action_available = False
    state.rage_expires_round = round_number + 1
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor_id,
        actor_name=state.template.name,
        feature_id=RAGE_EFFECT_ID,
        animation="rage",
        description=f"{state.template.name} extends Rage with a Bonus Action.",
    )


def end_rage(state: CombatantState) -> None:
    if not rage_active(state):
        return
    state.active_effect_ids.remove(RAGE_EFFECT_ID)
    state.temporary_damage_resistances = [
        damage_type
        for damage_type in state.temporary_damage_resistances
        if damage_type not in _RAGE_RESISTANCES
    ]
    state.rage_expires_round = None


def finish_rage_turn(state: CombatantState, round_number: int) -> None:
    if rage_active(state) and state.rage_expires_round is not None:
        if state.rage_expires_round <= round_number:
            end_rage(state)


def end_rage_if_incapacitated(state: CombatantState) -> None:
    if state.is_unconscious or state.is_dead:
        end_rage(state)
