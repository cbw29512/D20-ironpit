from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.support_effects import sanctuary_dc
from app.domain.models import CombatantState, DiceRoll


def sanctuary_targeting_save(
    attacker: CombatantState,
    defender: CombatantState,
    dice: DiceProvider,
) -> tuple[DiceRoll | None, bool, int | None]:
    dc = sanctuary_dc(defender)
    if dc is None:
        return None, True, None
    roll, succeeded = resolve_saving_throw(attacker, "wisdom", dc, dice)
    return roll, succeeded, dc
