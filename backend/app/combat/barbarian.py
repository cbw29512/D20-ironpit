from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import is_incapacitated
from app.combat.exhaustion import gain_exhaustion
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack

RAGE_EFFECT_ID = "rage"
FRENZY_2014_EFFECT_ID = "frenzy-2014"
_RAGE_RESISTANCES = (DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING)
_MINDLESS_RAGE_IMMUNITIES = {"charmed", "frightened"}


def _rage_resource(state: CombatantState):
    return next((resource for resource in state.resources if resource.id == "rage"), None)


def _rage_max_rounds(state: CombatantState) -> int:
    return 10 if state.template.ruleset == "2014" else 100


def rage_active(state: CombatantState) -> bool:
    return RAGE_EFFECT_ID in state.active_effect_ids


def rage_damage_bonus(state: CombatantState, attack: WeaponAttack) -> int:
    return state.template.rage_damage_bonus if rage_active(state) and attack.rage_eligible else 0


def _end_mindless_rage_conditions(state: CombatantState) -> list[str]:
    if not state.template.progression_features.mindless_rage:
        return []
    if state.template.ruleset == "2014":
        return []  # 2014 suppresses these conditions while Rage is active; it does not end them.
    removed = sorted(_MINDLESS_RAGE_IMMUNITIES.intersection(state.active_effect_ids))
    if not removed:
        return []
    state.timed_effects = [effect for effect in state.timed_effects if effect.effect_id not in removed]
    state.active_effect_ids = [effect_id for effect_id in state.active_effect_ids if effect_id not in removed]
    return removed


def enter_rage(sequence: int, round_number: int, state: CombatantState, actor_id: str) -> BattleEvent | None:
    """Use a Bonus Action and one Rage use, applying edition-correct Rage duration and Berserker policy."""
    if state.template.wearing_heavy_armor or state.template.rage_damage_bonus <= 0 or rage_active(state):
        return None
    resource = _rage_resource(state)
    if resource is None or resource.current_uses <= 0 or not is_available(state, "bonus_action"):
        return None
    resource.current_uses -= 1
    spend(state, "bonus_action")
    state.active_effect_ids.append(RAGE_EFFECT_ID)
    frenzy_2014 = state.template.ruleset == "2014" and state.template.progression_features.frenzy_bonus_attack_2014
    if frenzy_2014:
        state.active_effect_ids.append(FRENZY_2014_EFFECT_ID)
    removed = _end_mindless_rage_conditions(state)
    for damage_type in _RAGE_RESISTANCES:
        if damage_type not in state.temporary_damage_resistances:
            state.temporary_damage_resistances.append(damage_type)
    state.rage_expires_round = round_number + 1
    state.rage_max_round = round_number + _rage_max_rounds(state)
    description = f"{state.template.name} enters Rage."
    if frenzy_2014:
        description += " The Berserker enters a Frenzy."
    if removed:
        description += f" Mindless Rage ends {', '.join(removed)}."
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id=RAGE_EFFECT_ID,
        removed_condition_ids=removed, resource_remaining=resource.current_uses, animation="rage",
        description=description,
    )


def extend_rage_from_attack(state: CombatantState, round_number: int) -> None:
    if rage_active(state):
        maximum = state.rage_max_round or round_number + 1
        state.rage_expires_round = min(round_number + 1, maximum)


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
    maximum = state.rage_max_round or round_number + 1
    state.rage_expires_round = min(round_number + 1, maximum)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id=RAGE_EFFECT_ID,
        animation="rage", description=f"{state.template.name} extends Rage with a Bonus Action.",
    )


def end_rage(state: CombatantState) -> int | None:
    if not rage_active(state):
        return None
    frenzied = FRENZY_2014_EFFECT_ID in state.active_effect_ids
    state.active_effect_ids = [
        effect_id for effect_id in state.active_effect_ids
        if effect_id not in {RAGE_EFFECT_ID, FRENZY_2014_EFFECT_ID}
    ]
    state.temporary_damage_resistances = [d for d in state.temporary_damage_resistances if d not in _RAGE_RESISTANCES]
    state.rage_expires_round = None
    state.rage_max_round = None
    return gain_exhaustion(state) if frenzied else None


def finish_rage_turn(state: CombatantState, round_number: int) -> int | None:
    if rage_active(state) and state.rage_expires_round is not None and state.rage_expires_round <= round_number:
        return end_rage(state)
    return None


def finalize_rage_turn(
    sequence: int, round_number: int, state: CombatantState, actor_id: str,
) -> tuple[BattleEvent | None, int]:
    event = maintain_rage_with_bonus_action(sequence, round_number, state, actor_id)
    if event is not None:
        return event, sequence + 1
    exhaustion_level = finish_rage_turn(state, round_number)
    if exhaustion_level is None:
        return None, sequence
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor_id, actor_name=state.template.name, feature_id="exhaustion",
        animation="condition", description=(
            f"{state.template.name}'s Frenzy ends and causes Exhaustion level {exhaustion_level}."
        ),
    ), sequence + 1


def end_rage_if_incapacitated(state: CombatantState) -> None:
    if state.template.wearing_heavy_armor or state.is_dead or is_incapacitated(state):
        end_rage(state)
