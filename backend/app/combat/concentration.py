from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.support_effects import break_concentration, concentrating
from app.domain.models import CombatantState, DiceRoll, EncounterSetup


def concentration_after_damage(
    combatant_id: str,
    state: CombatantState,
    setup: EncounterSetup | None,
    damage: int,
    dice: DiceProvider,
) -> tuple[DiceRoll | None, bool | None, int | None]:
    if setup is None or damage <= 0 or not concentrating(combatant_id, setup):
        return None, None, None
    if state.is_dead or is_incapacitated(state):
        break_concentration(combatant_id, setup)
        return None, False, None
    dc = min(30, max(10, damage // 2))
    roll, succeeded = resolve_saving_throw(state, "constitution", dc, dice)
    if not succeeded:
        break_concentration(combatant_id, setup)
    return roll, succeeded, dc
