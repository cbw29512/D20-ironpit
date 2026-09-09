from __future__ import annotations

from typing import NamedTuple

from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.effect_gates import EffectGate
from app.domain.events import DiceRoll
from app.domain.runtime import CombatantState


class EffectGateResult(NamedTuple):
    passes: bool
    save_roll: DiceRoll | None = None
    save_succeeded: bool | None = None


def evaluate_effect_gate(
    target: CombatantState,
    gate: EffectGate,
    dice: DiceProvider | None = None,
) -> EffectGateResult:
    tags = {tag.casefold() for tag in target.template.creature_tags}
    creature_type = (target.template.creature_type or "").casefold()
    if any(tag.casefold() not in tags for tag in gate.required_target_tags):
        return EffectGateResult(False)
    if tags.intersection(tag.casefold() for tag in gate.excluded_target_tags):
        return EffectGateResult(False)
    if creature_type and creature_type in {item.casefold() for item in gate.excluded_creature_types}:
        return EffectGateResult(False)
    if gate.save_ability is None:
        return EffectGateResult(True)
    if dice is None:
        raise ValueError("Save-gated effect requires a dice provider.")
    if gate.save_dc is None:
        raise ValueError("Save-gated effect requires a save DC.")
    roll, succeeded = resolve_saving_throw(target, gate.save_ability, gate.save_dc, dice)
    return EffectGateResult(not succeeded, roll, succeeded)
