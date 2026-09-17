from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import is_incapacitated
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack

RAGE_EFFECT_ID = "rage"
FRENZY_2014_EFFECT_ID = "frenzy-2014"
_RAGE_2024_MAX_ROUNDS = 100
_RAGE_RESISTANCES = (DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING)
_MINDLESS_RAGE_IMMUNITIES = {"charmed", "frightened"}


def _rage_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == "rage"), None)


def _is_2014(state: CombatantState) -> bool:
    return state.template.ruleset == "2014"


def rage_active(state: CombatantState) -> bool:
    return RAGE_EFFECT_ID in state.active_effect_ids


def rage_damage_bonus(state: CombatantState, attack: WeaponAttack) -> int:
    return state.template.rage_damage_bonus if rage_active(state) and attack.rage_eligible else 0


def _end_mindless_rage_conditions(state: CombatantState) -> list[str]:
    if not state.template.progression_features.mindless_rage or _is_2014(state):
        return []
    removed = sorted(_MINDLESS_RAGE_IMMUNITIES.intersection(state.active_effect_ids))
    if not removed:
        return []
    state.timed_effects = [effect for effect in state.timed_effects if effect.effect_id not in removed]
    state.active_effect_ids = [effect_id for effect_id in state.active_effect_ids if effect_id not in removed]
    return removed


def enter_rage(sequence: int, round_number: int, state: CombatantState, actor_id: str) -> BattleEvent | None:
    if state.template.wearing_heavy_armor or state.template.rage_damage_bonus <= 0 or rage_active(state):
        return None
    resource = _rage_resource(state)
    if resource is None or resource.current_uses <= 0 or not is_available(state, "bonus_action"):
        return None
    resource.current_uses -= 1; spend(state, "bonus_action")
    state.active_effect_ids.append(RAGE_EFFECT_ID)
    removed = _end_mindless_rage_conditions(state)
    for damage_type in _RAGE_RESISTANCES:
        if damage_type not in state.temporary_damage_resistances:
            state.temporary_damage_resistances.append(damage_type)
    state.rage_started_round = round_number
    state.rage_last_attack_round = None; state.rage_last_damage_round = None
    state.rage_expires_round = round_number + 1
    state.rage_max_round = round_number + (9 if _is_2014(state) else _RAGE_2024_MAX_ROUNDS)
    if _is_2014(state) and state.template.progression_features.frenzy_bonus_attack_2014:
        if FRENZY_2014_EFFECT_ID not in state.active_effect_ids:
            state.active_effect_ids.append(FRENZY_2014_EFFECT_ID)
        state.frenzy_2014_started_round = round_number
    description = f"{state.template.name} enters Rage."
    if state.frenzy_2014_started_round == round_number:
        description += " Frenzy is active."
    if removed:
        description += f" Mindless Rage ends {', '.join(removed)}."
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature", actor_id=actor_id,
        actor_name=state.template.name, feature_id=RAGE_EFFECT_ID, removed_condition_ids=removed,
        resource_remaining=resource.current_uses, animation="rage", description=description,
    )


def extend_rage_from_attack(state: CombatantState, round_number: int) -> None:
    if not rage_active(state):
        return
    state.rage_last_attack_round = round_number
    maximum = state.rage_max_round or round_number + 1
    state.rage_expires_round = min(round_number + 1, maximum)


def note_rage_damage(state: CombatantState, round_number: int) -> None:
    if rage_active(state) and _is_2014(state):
        state.rage_last_damage_round = round_number


def _end_frenzy_2014(state: CombatantState) -> None:
    if FRENZY_2014_EFFECT_ID not in state.active_effect_ids:
        return
    state.active_effect_ids.remove(FRENZY_2014_EFFECT_ID)
    state.frenzy_2014_started_round = None
    state.exhaustion_level_2014 = min(6, state.exhaustion_level_2014 + 1)
    if state.exhaustion_level_2014 >= 6:
        state.current_hp = 0; state.is_alive = False; state.is_dead = True; state.is_unconscious = False


def end_rage(state: CombatantState) -> None:
    if not rage_active(state):
        return
    if _is_2014(state):
        _end_frenzy_2014(state)
    state.active_effect_ids.remove(RAGE_EFFECT_ID)
    state.temporary_damage_resistances = [d for d in state.temporary_damage_resistances if d not in _RAGE_RESISTANCES]
    state.rage_expires_round = None; state.rage_max_round = None; state.rage_started_round = None
    state.rage_last_attack_round = None; state.rage_last_damage_round = None


def finalize_rage_turn(sequence: int, round_number: int, state: CombatantState, actor_id: str) -> tuple[BattleEvent | None, int]:
    if not rage_active(state) or state.rage_expires_round is None:
        return None, sequence
    if _is_2014(state):
        if state.rage_max_round is not None and round_number >= state.rage_max_round:
            end_rage(state); return None, sequence
        maintained = state.rage_last_attack_round == round_number or (
            state.rage_last_damage_round is not None and state.rage_last_damage_round >= round_number - 1
        )
        if maintained:
            state.rage_expires_round = min(round_number + 1, state.rage_max_round or round_number + 1)
        elif state.rage_expires_round <= round_number:
            end_rage(state)
        return None, sequence
    if state.rage_max_round is not None and state.rage_max_round <= round_number:
        end_rage(state); return None, sequence
    if state.rage_expires_round > round_number or not is_available(state, "bonus_action"):
        if state.rage_expires_round <= round_number:
            end_rage(state)
        return None, sequence
    spend(state, "bonus_action")
    state.rage_expires_round = min(round_number + 1, state.rage_max_round or round_number + 1)
    event = BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature", actor_id=actor_id,
        actor_name=state.template.name, feature_id=RAGE_EFFECT_ID, animation="rage",
        description=f"{state.template.name} extends Rage with a Bonus Action.",
    )
    return event, sequence + 1


def end_rage_if_incapacitated(state: CombatantState) -> None:
    if state.template.wearing_heavy_armor or state.is_dead or is_incapacitated(state):
        end_rage(state)
