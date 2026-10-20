"""Universal target-choice saving throw selection from live battle modifiers."""
from __future__ import annotations

import logging

from app.combat.ability_score_reduction import ability_modifier_delta
from app.combat.modifier_stack import saving_throw_flat_bonus
from app.combat.saving_throw_rolls import saving_throw_mode
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def choose_save_ability(state, abilities, dc, context=None, *, member=None, setup=None) -> str:
    """Choose the highest d20 success probability, before spending/rolling dice."""
    try:
        if not abilities:
            raise ValueError("Save ability choice requires two or more declared abilities.")
        context = context or SavingThrowContext()
        best_ability = None
        best_chance = -1.0
        for ability in abilities:
            base_bonus = state.template.saving_throw_bonuses.get(ability)
            if base_bonus is None:
                raise ValueError(f"Missing certified {ability} saving throw bonus.")
            bonus = (
                base_bonus + ability_modifier_delta(state, ability)
                + saving_throw_flat_bonus(state, ability)
            )
            p = max(0.0, min(1.0, (21 + bonus - dc) / 20.0))
            mode = saving_throw_mode(state, ability, context, member=member, setup=setup)
            mode_name = getattr(mode, "value", mode)
            if mode_name == "advantage":
                p = 1 - (1 - p) ** 2
            elif mode_name == "disadvantage":
                p = p ** 2
            elif mode_name != "normal":
                raise ValueError(f"Unsupported saving-throw mode: {mode_name}")
            if p > best_chance:
                best_ability, best_chance = ability, p
        if best_ability is None:
            raise ValueError("No supported saving throw choice.")
        return best_ability
    except Exception:
        logger.exception("Failed target-selected saving throw: %s", abilities)
        raise
