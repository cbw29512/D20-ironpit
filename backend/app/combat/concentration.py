from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.modifier_stack import remove_source_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.events import DiceRoll
from app.domain.modifiers import ConcentrationState
from app.domain.runtime import CombatantState


@dataclass(frozen=True)
class ConcentrationCheck:
    dc: int | None
    roll: DiceRoll | None
    succeeded: bool
    ended: bool
    reason: str


def concentration_dc(damage_taken: int) -> int:
    if damage_taken < 0:
        raise ValueError("Concentration damage cannot be negative.")
    return min(30, max(10, damage_taken // 2))


def _affected(owner: CombatantState, states: Iterable[CombatantState] | None) -> list[CombatantState]:
    affected = list(states or [])
    if not any(item is owner for item in affected):
        affected.append(owner)
    return affected


def end_concentration(
    owner: CombatantState,
    affected_states: Iterable[CombatantState] | None = None,
) -> bool:
    current = owner.concentration
    if current is None:
        return False
    remove_source_modifiers(
        _affected(owner, affected_states),
        current.source_id,
        current.effect_id,
        concentration_only=True,
    )
    owner.concentration = None
    return True


def start_concentration(
    owner: CombatantState,
    source_id: str,
    effect_id: str,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
    expires_round: int | None = None,
) -> ConcentrationState:
    if owner.is_dead or is_incapacitated(owner):
        raise ValueError("An Incapacitated or dead creature cannot start Concentration.")
    if expires_round is not None and expires_round <= round_number:
        raise ValueError("Concentration expiry must be after the start round.")
    end_concentration(owner, affected_states)
    owner.concentration = ConcentrationState(
        source_id=source_id,
        effect_id=effect_id,
        started_round=round_number,
        expires_round=expires_round,
    )
    return owner.concentration


def end_concentration_if_incapacitated(
    owner: CombatantState,
    affected_states: Iterable[CombatantState] | None = None,
) -> bool:
    if owner.concentration is None or (not owner.is_dead and not is_incapacitated(owner)):
        return False
    return end_concentration(owner, affected_states)


def end_concentration_if_expired(
    owner: CombatantState,
    round_number: int,
    affected_states: Iterable[CombatantState] | None = None,
) -> bool:
    current = owner.concentration
    if current is None or current.expires_round is None or round_number < current.expires_round:
        return False
    return end_concentration(owner, affected_states)


def resolve_concentration_damage(
    owner: CombatantState,
    damage_taken: int,
    dice: DiceProvider,
    affected_states: Iterable[CombatantState] | None = None,
) -> ConcentrationCheck | None:
    if damage_taken < 0:
        raise ValueError("Concentration damage cannot be negative.")
    if owner.concentration is None or damage_taken == 0:
        return None
    if owner.is_dead or is_incapacitated(owner):
        end_concentration(owner, affected_states)
        return ConcentrationCheck(None, None, False, True, "incapacitated-or-dead")
    dc = concentration_dc(damage_taken)
    roll, succeeded = resolve_saving_throw(owner, "constitution", dc, dice)
    if not succeeded:
        end_concentration(owner, affected_states)
    return ConcentrationCheck(dc, roll, succeeded, not succeeded, "damage")
