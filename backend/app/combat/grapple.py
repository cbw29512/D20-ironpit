from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import rage_active
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import condition_speed_is_zero, has_condition
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.combat.tactical_mind import apply_tactical_mind
from app.domain.models import BattleEvent, CombatantState, EncounterSetup, GrappleSource, RollMode

FRIGHTENED_EFFECT_ID = "frightened"
GRAPPLED_EFFECT_ID = "grappled"
POISONED_EFFECT_ID = "poisoned"
RESTRAINED_EFFECT_ID = "restrained"


def _sync_effect_ids(state: CombatantState) -> None:
    if state.grapple_sources:
        if GRAPPLED_EFFECT_ID not in state.active_effect_ids:
            state.active_effect_ids.append(GRAPPLED_EFFECT_ID)
        if "dodge" in state.active_effect_ids:
            state.active_effect_ids.remove("dodge")
    elif GRAPPLED_EFFECT_ID in state.active_effect_ids:
        state.active_effect_ids.remove(GRAPPLED_EFFECT_ID)
    restrained = any(source.restrains for source in state.grapple_sources)
    if restrained and RESTRAINED_EFFECT_ID not in state.active_effect_ids:
        state.active_effect_ids.append(RESTRAINED_EFFECT_ID)
    elif not restrained and RESTRAINED_EFFECT_ID in state.active_effect_ids:
        state.active_effect_ids.remove(RESTRAINED_EFFECT_ID)


def apply_grapple(
    state: CombatantState, source_id: str, escape_dc: int, range_ft: int, *, restrains: bool = False,
) -> list[str]:
    if condition_is_immune(state, GRAPPLED_EFFECT_ID):
        return []
    state.grapple_sources = [source for source in state.grapple_sources if source.source_id != source_id]
    restrains = restrains and not condition_is_immune(state, RESTRAINED_EFFECT_ID)
    state.grapple_sources.append(GrappleSource(
        source_id=source_id, escape_dc=escape_dc, range_ft=range_ft, restrains=restrains,
    ))
    _sync_effect_ids(state)
    return [GRAPPLED_EFFECT_ID, RESTRAINED_EFFECT_ID] if restrains else [GRAPPLED_EFFECT_ID]


def release_grapple(state: CombatantState, source_id: str) -> None:
    state.grapple_sources = [source for source in state.grapple_sources if source.source_id != source_id]
    _sync_effect_ids(state)


def speed_is_zero(state: CombatantState) -> bool:
    return bool(state.grapple_sources) or condition_speed_is_zero(state)


def grapple_attack_disadvantage(state: CombatantState, target_id: str) -> int:
    if not state.grapple_sources:
        return 0
    return 0 if any(source.source_id == target_id for source in state.grapple_sources) else 1


def cleanup_grapples(setup: EncounterSetup) -> None:
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    for target in members.values():
        retained: list[GrappleSource] = []
        for source in target.state.grapple_sources:
            grappler = members.get(source.source_id)
            if grappler is None or grappler.state.is_dead or grappler.state.is_unconscious:
                continue
            if abs(grappler.position_ft - target.position_ft) > source.range_ft:
                continue
            retained.append(source)
        target.state.grapple_sources = retained
        _sync_effect_ids(target.state)


def should_escape_grapple(state: CombatantState) -> bool:
    return is_available(state, "action") and any(source.restrains for source in state.grapple_sources)


def _check_mode(state: CombatantState, strength_check: bool) -> RollMode:
    advantage = strength_check and (
        rage_active(state) or state.template.progression_features.athletics_advantage
    )
    disadvantage = has_condition(state, POISONED_EFFECT_ID) or has_condition(state, FRIGHTENED_EFFECT_ID)
    if advantage == disadvantage:
        return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def _escape_choice(state: CombatantState) -> tuple[str, int, RollMode]:
    athletics = state.template.skill_bonuses.get("athletics")
    acrobatics = state.template.skill_bonuses.get("acrobatics")
    if athletics is None and acrobatics is None:
        raise ValueError(f"{state.template.name} lacks certified Athletics/Acrobatics bonuses.")
    if athletics is not None and (acrobatics is None or athletics >= acrobatics):
        return "strength (athletics)", athletics, _check_mode(state, True)
    return "dexterity (acrobatics)", int(acrobatics), _check_mode(state, False)


def resolve_escape_grapple(
    sequence: int, round_number: int, actor_id: str, state: CombatantState, dice: DiceProvider,
) -> BattleEvent:
    if not is_available(state, "action"):
        raise ValueError("Action is not available to escape a grapple.")
    source = next((item for item in state.grapple_sources if item.restrains), state.grapple_sources[0])
    check_name, bonus, mode = _escape_choice(state)
    check = roll_d20(dice, bonus, mode)
    success = check.total >= source.escape_dc
    tactical_used = False
    if not success:
        check, tactical_used, success = apply_tactical_mind(state, check, source.escape_dc, dice)
    spend(state, "action")
    if success:
        release_grapple(state, source.source_id)
        if not speed_is_zero(state):
            state.movement_remaining_ft = max(state.movement_remaining_ft, state.template.speed_ft)
    second_wind = next((item for item in state.resources if item.id == "second-wind"), None)
    tactical = " after using Tactical Mind" if tactical_used else ""
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature", actor_id=actor_id,
        actor_name=state.template.name, target_id=source.source_id, ability_check_roll=check,
        check_ability=check_name, check_dc=source.escape_dc, check_succeeded=success,
        feature_id="escape-grapple", resource_remaining=second_wind.current_uses if tactical_used and second_wind else None,
        animation="escape-grapple",
        description=(f"{state.template.name} {'escapes' if success else 'fails to escape'} the grapple{tactical} "
                     f"with {check_name.title()} against DC {source.escape_dc}."),
    )
