from __future__ import annotations

from app.combat.ability_scores import apply_ability_score_reduction
from app.combat.attack_ability_bonus import effective_attack_bonus
from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, WeaponAttack


def resolve_attack_ability_reduction(
    attack: WeaponAttack,
    target: CombatantState,
    dice: DiceProvider,
    affected_states: list[CombatantState] | None,
) -> tuple[int, int, int] | None:
    effect = attack.ability_score_reduction_on_hit
    if effect is None:
        return None
    return apply_ability_score_reduction(target, effect, dice, affected_states)


__all__ = ["effective_attack_bonus", "resolve_attack_ability_reduction"]
