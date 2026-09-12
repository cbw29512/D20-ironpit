from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import rage_active
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition
from app.combat.d20_effects import strength_d20_disadvantage
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.combat.tactical_mind import apply_tactical_mind
from app.domain.models import BattleEvent, CombatantState, RollMode, WeaponAttack
from app.domain.restraints import RestraintState
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _sync_condition(state: CombatantState, condition_id: str) -> None:
    active = any(item.condition_id == condition_id for item in state.restraint_sources)
    if active and condition_id not in state.active_effect_ids:
        state.active_effect_ids.append(condition_id)
    if not active and condition_id in state.active_effect_ids:
        state.active_effect_ids.remove(condition_id)


def apply_breakable_restraint(state: CombatantState, source_id: str, attack: WeaponAttack) -> list[str]:
    try:
        profile = attack.breakable_restraint
        if profile is None or condition_is_immune(state, profile.condition_id):
            return []
        if profile.max_target_size is not None and not size_at_most(state.template.size, profile.max_target_size):
            return []
        state.restraint_sources = [
            item for item in state.restraint_sources
            if not (item.source_id == source_id and item.source_effect_id == attack.id)
        ]
        state.restraint_sources.append(RestraintState(
            source_id=source_id, source_effect_id=attack.id, condition_id=profile.condition_id,
            escape_ability=profile.escape_ability, escape_dc=profile.escape_dc,
            object_ac=profile.object_ac, current_hp=profile.object_hp, max_hp=profile.object_hp,
            damage_vulnerabilities=profile.damage_vulnerabilities, damage_immunities=profile.damage_immunities,
        ))
        _sync_condition(state, profile.condition_id)
        return [profile.condition_id]
    except Exception as exc:
        logger.exception("Failed to apply breakable restraint from %s.", attack.id)
        raise RuntimeError("Breakable restraint could not be applied.") from exc


def release_restraint(state: CombatantState, source: RestraintState) -> None:
    state.restraint_sources = [item for item in state.restraint_sources if item != source]
    _sync_condition(state, source.condition_id)


def should_escape_restraint(state: CombatantState) -> bool:
    return is_available(state, "action") and bool(state.restraint_sources)


def _check_mode(state: CombatantState, ability: str) -> RollMode:
    advantage = ability == "strength" and rage_active(state)
    disadvantage = has_condition(state, "poisoned") or has_condition(state, "frightened")
    if ability == "strength": disadvantage = disadvantage or bool(strength_d20_disadvantage(state))
    if advantage == disadvantage: return RollMode.NORMAL
    return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE


def resolve_escape_restraint(
    sequence: int, round_number: int, actor_id: str, state: CombatantState, dice: DiceProvider,
) -> BattleEvent:
    try:
        if not should_escape_restraint(state):
            raise ValueError("Action is unavailable or no breakable restraint is active.")
        source = state.restraint_sources[0]
        bonus = state.template.ability_scores.modifier(source.escape_ability)
        check = roll_d20(dice, bonus, _check_mode(state, source.escape_ability))
        success = check.total >= source.escape_dc; tactical_used = False
        if not success:
            check, tactical_used, success = apply_tactical_mind(state, check, source.escape_dc, dice)
        spend(state, "action")
        if success: release_restraint(state, source)
        second_wind = next((item for item in state.resources if item.id == "second-wind"), None)
        tactical = " after using Tactical Mind" if tactical_used else ""
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature", actor_id=actor_id,
            actor_name=state.template.name, target_id=source.source_id, ability_check_roll=check,
            check_ability=source.escape_ability, check_dc=source.escape_dc, check_succeeded=success,
            feature_id="escape-restraint", resource_remaining=second_wind.current_uses if tactical_used and second_wind else None,
            animation="escape-restraint",
            description=(f"{state.template.name} {'escapes' if success else 'fails to escape'} {source.source_effect_id}{tactical} "
                         f"with a {source.escape_ability.title()} check against DC {source.escape_dc}."),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Breakable restraint escape failed for %s.", actor_id)
        raise RuntimeError("Breakable restraint escape could not be resolved.") from exc
