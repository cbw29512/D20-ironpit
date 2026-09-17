from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import is_incapacitated
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack

RAGE_EFFECT_ID = "rage"
_RAGE_MAX_ROUNDS_2014 = 10
_RAGE_MAX_ROUNDS_2024 = 100
_RAGE_RESISTANCES = (DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING)
_MINDLESS_RAGE_IMMUNITIES = {"charmed", "frightened"}


def _rage_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == "rage"), None)


def _rage_max_rounds(state: CombatantState) -> int:
    return _RAGE_MAX_ROUNDS_2014 if state.template.ruleset == "2014" else _RAGE_MAX_ROUNDS_2024


def rage_active(state: CombatantState) -> bool:
    return RAGE_EFFECT_ID in state.active_effect_ids


def rage_damage_bonus(state: CombatantState, attack: WeaponAttack) -> int:
    return state.template.rage_damage_bonus if rage_active(state) and attack.rage_eligible else 0


def _end_mindless_rage_conditions(state: CombatantState) -> list[str]:
    if not state.template.progression_features.mindless_rage:
        return []
    removed = sorted(_MINDLESS_RAGE_IMMUNITIES.intersection(state.active_effect_ids))
    if not removed:
        return []
    state.timed_effects = [effect for effect in state.timed_effects if effect.effect_id not in removed]
    state.active_effect_ids = [effect_id for effect_id in state.active_effect_ids if effect_id not in removed]
    return removed


def enter_rage(sequence: int, round_number: int, state: CombatantState, actor_id: str) -> BattleEvent | None:
    """Spend a Bonus Action and Rage use, then apply edition-correct Rage duration."""
    if state.template.wearing_heavy_armor or state.template.rage_damage_bonus <= 0 or rage_active(state):
        return None
    resource = _rage_resource(state)
    if resource is None or resource.current_uses <= 0 or not is_available(state, "bonus_action"):
        return None
    resource.current_uses -= 1
    spend(state, "bonus_action")
    state.active_effect_ids.append(RAGE_EFFECT_ID)
    removed = _end_mindless_rage_conditions(state)
    for damage_type in _RAGE_RESISTANCES:
        if damage_type not in state.temporary_damage_resistances:
            state.temporary_damage_resistances.append(damage_type)
    state.rage_expires_round = round_number + 1
    state.rage_max_round = round_number + _rage_max_rounds(state)
    description = f"{state.template.name} enters Rage."
    if removed:
        description += f" Mindless Rage ends {', '.join(removed)}."
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id=RAGE_EFFECT_ID,
        removed_condition_ids=removed, resource_remaining=resource.current_uses, animation="rage",
        description=description,
    )


def _extend_rage(state: CombatantState, round_number: int) -> None:
    maximum = state.rage_max_round or round_number + 1
    state.rage_expires_round = min(round_number + 1, maximum)


def extend_rage_from_attack(state: CombatantState, round_number: int) -> None:
    if rage_active(state):
        _extend_rage(state, round_number)


def extend_rage_from_damage(state: CombatantState, round_number: int) -> None:
    """2014 Rage persists when the barbarian has taken damage since its previous turn."""
    if state.template.ruleset == "2014" and rage_active(state):
        _extend_rage(state, round_number)


def maintain_rage_with_bonus_action(
    sequence: int, round_number: int, state: CombatantState, actor_id: str,
) -> BattleEvent | None:
    if state.template.ruleset == "2014":
        return None
    if not rage_active(state) or state.rage_expires_round is None:
        return None
    if state.rage_max_round is not None and state.rage_max_round <= round_number:
        return None
    if state.rage_expires_round > round_number or not is_available(state, "bonus_action"):
        return None
    spend(state, "bonus_action")
    _extend_rage(state, round_number)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id=RAGE_EFFECT_ID,
        animation="rage", description=f"{state.template.name} extends Rage with a Bonus Action.",
    )


def end_rage(state: CombatantState) -> None:
    if not rage_active(state):
        return
    state.active_effect_ids.remove(RAGE_EFFECT_ID)
    state.temporary_damage_resistances = [d for d in state.temporary_damage_resistances if d not in _RAGE_RESISTANCES]
    state.rage_expires_round = None
    state.rage_max_round = None


def finish_rage_turn(state: CombatantState, round_number: int) -> None:
    if rage_active(state) and state.rage_expires_round is not None and state.rage_expires_round <= round_number:
        end_rage(state)


def finalize_rage_turn(
    sequence: int, round_number: int, state: CombatantState, actor_id: str,
) -> tuple[BattleEvent | None, int]:
    event = maintain_rage_with_bonus_action(sequence, round_number, state, actor_id)
    if event is not None:
        sequence += 1
    finish_rage_turn(state, round_number)
    return event, sequence


def end_rage_if_incapacitated(state: CombatantState) -> None:
    if state.template.wearing_heavy_armor or state.is_dead or is_incapacitated(state):
        end_rage(state)
