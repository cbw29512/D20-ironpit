from __future__ import annotations

import logging

from app.combat.barbarian_modifiers import rage_strength_save_advantage
from app.combat.conditions import automatically_fails_save, condition_save_disadvantage
from app.combat.cover import resolve_dex_save_cover_bonus
from app.combat.dice import DiceProvider
from app.combat.dodge import dodge_save_advantage
from app.combat.rolls import resolve_roll_mode, roll_d20
from app.domain.models import AbilityKind, BattlefieldState, CombatantState, SavingThrowResult

logger = logging.getLogger(__name__)


def saving_throw_bonus(state: CombatantState, ability: AbilityKind) -> int:
    try:
        if ability not in state.template.ability_modifiers:
            raise ValueError(f"{state.template.name} is missing its {ability.value} modifier.")
        bonus = state.template.ability_modifiers[ability]
        if ability in state.template.saving_throw_proficiencies:
            bonus += state.template.proficiency_bonus
        return bonus
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Saving throw bonus failed for %s.", state.template.name)
        raise RuntimeError("Saving throw bonus could not be resolved.") from exc


def resolve_saving_throw(
    state: CombatantState,
    ability: AbilityKind,
    dc: int,
    dice: DiceProvider,
    *,
    advantage_sources: int = 0,
    disadvantage_sources: int = 0,
    circumstantial_modifier: int = 0,
    battlefield: BattlefieldState | None = None,
    choose_failure: bool = False,
) -> SavingThrowResult:
    try:
        if dc < 0:
            raise ValueError("Saving throw DC cannot be negative.")
        if choose_failure:
            return SavingThrowResult(
                ability=ability,
                dc=dc,
                success=False,
                chosen_failure=True,
                circumstantial_modifier=circumstantial_modifier,
            )
        if automatically_fails_save(state, ability):
            return SavingThrowResult(
                ability=ability,
                dc=dc,
                success=False,
                automatic_failure=True,
                circumstantial_modifier=circumstantial_modifier,
            )

        cover_bonus = 0
        if ability is AbilityKind.DEXTERITY:
            cover_bonus = resolve_dex_save_cover_bonus(state, battlefield)
        modifier = saving_throw_bonus(state, ability) + circumstantial_modifier + cover_bonus
        dodge_advantage = dodge_save_advantage(state, ability)
        rage_advantage = rage_strength_save_advantage(state, ability)
        condition_disadvantage = condition_save_disadvantage(state, ability)
        mode = resolve_roll_mode(
            advantage_sources + dodge_advantage + rage_advantage,
            disadvantage_sources + condition_disadvantage,
        )
        roll = roll_d20(dice, modifier, mode)
        return SavingThrowResult(
            ability=ability,
            dc=dc,
            roll=roll,
            success=roll.total >= dc,
            circumstantial_modifier=circumstantial_modifier,
            cover_bonus=cover_bonus,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Saving throw failed for %s.", state.template.name)
        raise RuntimeError("Saving throw could not be resolved.") from exc
