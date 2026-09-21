from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.modifier_stack import apply_d20_bonus_dice, saving_throw_flat_bonus
from app.combat.rolls import roll_d20
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.models import CombatantState, DiceRoll
from app.domain.modifiers import ModifierKind


def _config(state: CombatantState) -> tuple[str, str, int] | None:
    progression = state.template.progression_features
    if progression.failed_save_reroll_resource_id:
        source = progression.failed_save_reroll_source_id or progression.failed_save_reroll_resource_id
        return source, progression.failed_save_reroll_resource_id, progression.failed_save_reroll_bonus
    if progression.indomitable_reroll or progression.indomitable_bonus > 0:
        return "indomitable", "indomitable", progression.indomitable_bonus
    return None


def use_failed_save_reroll(
    state: CombatantState, ability: str, dice: DiceProvider,
) -> tuple[DiceRoll, str] | None:
    """Spend the configured resource and reroll one failed saving throw."""
    config = _config(state)
    if config is None:
        return None
    source_id, resource_id, bonus = config
    resource = next((item for item in state.resources if item.id == resource_id), None)
    if resource is None or resource.current_uses <= 0:
        return None
    if ability not in state.template.saving_throw_bonuses:
        raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
    resource.current_uses -= 1
    roll = apply_d20_bonus_dice(
        state,
        ModifierKind.SAVING_THROW_BONUS_DIE,
        roll_d20(
            dice,
            state.template.saving_throw_bonuses[ability] + saving_throw_flat_bonus(state) + bonus,
            saving_throw_mode(state, ability),
        ),
        dice,
    )
    suffix = f" +{bonus}" if bonus else ""
    label = source_id.replace("-", " ").title()
    return roll.model_copy(update={"notation": f"{roll.notation} [{label}{suffix}]"}), source_id


def use_indomitable(state: CombatantState, ability: str, dice: DiceProvider) -> DiceRoll | None:
    """Compatibility wrapper for direct Fighter Indomitable callers."""
    progression = state.template.progression_features
    if not (progression.indomitable_reroll or progression.indomitable_bonus > 0):
        return None
    result = use_failed_save_reroll(state, ability, dice)
    return result[0] if result is not None else None
