from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.abilities import Ability, SKILL_ABILITY, Skill
from app.domain.models import CombatantState, DiceRoll

logger = logging.getLogger(__name__)


def ability_modifier(state: CombatantState, ability: Ability) -> int:
    try:
        if ability not in state.template.ability_modifiers:
            raise ValueError(f"Missing {ability.value} modifier for {state.template.id}.")
        return state.template.ability_modifiers[ability]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ability modifier lookup failed for %s.", state.template.id)
        raise RuntimeError("Ability modifier could not be resolved.") from exc


def saving_throw_modifier(state: CombatantState, ability: Ability) -> int:
    return state.template.saving_throw_modifiers.get(ability, ability_modifier(state, ability))


def skill_modifier(state: CombatantState, skill: Skill) -> int:
    return state.template.skill_modifiers.get(skill, ability_modifier(state, SKILL_ABILITY[skill]))


def resolve_saving_throw(
    state: CombatantState,
    ability: Ability,
    dc: int,
    dice: DiceProvider,
) -> tuple[DiceRoll, bool]:
    try:
        if dc < 1:
            raise ValueError("Saving throw DC must be positive.")
        roll = roll_d20(dice, saving_throw_modifier(state, ability))
        return roll, roll.total >= dc
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Saving throw failed for %s.", state.template.name)
        raise RuntimeError("Saving throw could not be resolved.") from exc


def resolve_ability_check(
    state: CombatantState,
    skill: Skill,
    dc: int,
    dice: DiceProvider,
) -> tuple[DiceRoll, bool]:
    try:
        if dc < 1:
            raise ValueError("Ability check DC must be positive.")
        roll = roll_d20(dice, skill_modifier(state, skill))
        return roll, roll.total >= dc
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ability check failed for %s.", state.template.name)
        raise RuntimeError("Ability check could not be resolved.") from exc


def choose_best_save(state: CombatantState, abilities: tuple[Ability, ...]) -> Ability:
    if not abilities:
        raise ValueError("At least one saving throw ability is required.")
    return max(abilities, key=lambda item: (saving_throw_modifier(state, item), -list(Ability).index(item)))
