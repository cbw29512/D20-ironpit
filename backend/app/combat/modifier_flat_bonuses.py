from __future__ import annotations

from app.combat.cover_modifiers import strongest_cover_bonus
from app.combat.timed_control_bonuses import timed_saving_throw_flat_bonus
from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState


def attack_roll_flat_bonus(state: CombatantState, weapon_id: str) -> int:
    return sum(
        item.flat_bonus for item in state.active_modifiers
        if item.kind is ModifierKind.ATTACK_ROLL_FLAT
        and (item.weapon_id is None or item.weapon_id == weapon_id)
    )


def weapon_damage_flat_bonus(state: CombatantState, weapon_id: str) -> int:
    return sum(
        item.flat_bonus for item in state.active_modifiers
        if item.kind is ModifierKind.WEAPON_DAMAGE_FLAT
        and (item.weapon_id is None or item.weapon_id == weapon_id)
    )


def saving_throw_flat_bonus(state: CombatantState, ability: str | None = None) -> int:
    stacking_bonus = sum(
        item.flat_bonus for item in state.active_modifiers
        if item.kind is ModifierKind.SAVING_THROW_FLAT
        and (item.save_ability is None or ability is None or item.save_ability == ability)
    )
    return stacking_bonus + timed_saving_throw_flat_bonus(state, ability) + strongest_cover_bonus(
        state, ModifierKind.COVER_SAVING_THROW_FLAT, ability,
    )
