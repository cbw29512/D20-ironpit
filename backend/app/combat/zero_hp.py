from __future__ import annotations

import logging
from typing import Literal

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.orc import use_relentless_endurance
from app.combat.undead_fortitude import resolve_undead_fortitude
from app.domain.models import CombatantState, DamageType
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
ZeroHpOutcome = Literal[
    "damaged", "unconscious", "dead", "unchanged", "relentless_endurance", "undead_fortitude",
]
DODGE_EFFECT_ID = "dodge"
PRONE_EFFECT_ID = "prone"


def reset_death_saves(state: CombatantState) -> None:
    state.death_save_successes = 0
    state.death_save_failures = 0


def _mark_dead(state: CombatantState) -> ZeroHpOutcome:
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != DODGE_EFFECT_ID]
    return "dead"


def _mark_unconscious(state: CombatantState) -> ZeroHpOutcome:
    state.is_alive = True
    state.is_unconscious = True
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != DODGE_EFFECT_ID]
    if not condition_is_immune(state, PRONE_EFFECT_ID) and PRONE_EFFECT_ID not in state.active_effect_ids:
        state.active_effect_ids.append(PRONE_EFFECT_ID)
    return "unconscious"


def _after_temporary_hp(state: CombatantState, amount: int) -> int:
    absorbed = min(state.temporary_hp, amount)
    state.temporary_hp -= absorbed
    return amount - absorbed


def restore_hit_points(state: CombatantState, amount: int) -> int:
    """Restore true HP; ordinary healing cannot restore a dead creature or a Swarm."""
    if amount < 0:
        raise ValueError("Healing cannot be negative.")
    if state.is_dead or amount == 0 or CombatTrait.SWARM in state.template.combat_traits:
        return 0
    before = state.current_hp
    state.current_hp = min(state.template.max_hp, before + amount)
    healed = state.current_hp - before
    if healed > 0:
        state.is_alive = True
        state.is_unconscious = False
        state.is_stable = False
        reset_death_saves(state)
    return healed


def _damage_at_zero(state: CombatantState, incoming: int, *, critical: bool) -> ZeroHpOutcome:
    if state.template.kind == "monster" or incoming >= state.template.max_hp:
        return _mark_dead(state)
    state.is_stable = False
    state.death_save_failures = min(3, state.death_save_failures + (2 if critical else 1))
    if state.death_save_failures >= 3:
        return _mark_dead(state)
    return _mark_unconscious(state)


def apply_damage(
    state: CombatantState,
    amount: int,
    *,
    critical: bool = False,
    damage_types: set[DamageType] | None = None,
    dice: DiceProvider | None = None,
) -> ZeroHpOutcome:
    """Apply Temporary HP and SRD 5.2.1 zero-HP prevention/lifecycle rules."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if amount == 0 or state.is_dead:
            return "unchanged"

        incoming = amount
        types = damage_types or set()
        amount = _after_temporary_hp(state, amount)
        if state.current_hp == 0:
            return _damage_at_zero(state, incoming, critical=critical)
        if amount == 0:
            return "damaged"

        hp_before = state.current_hp
        state.current_hp = max(0, hp_before - amount)
        if state.current_hp > 0:
            return "damaged"
        if resolve_undead_fortitude(
            state, incoming, types, critical=critical, dice=dice,
        ):
            return "undead_fortitude"
        if state.template.kind == "monster":
            return _mark_dead(state)

        remaining_damage = max(0, amount - hp_before)
        if remaining_damage >= state.template.max_hp:
            return _mark_dead(state)
        if use_relentless_endurance(state, remaining_damage):
            return "relentless_endurance"
        return _mark_unconscious(state)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Zero-HP damage resolution failed for %s.", state.template.name)
        raise RuntimeError("Zero-HP damage could not be resolved.") from exc
