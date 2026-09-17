from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState, DamageRollComponent


def apply_uncanny_dodge(
    state: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[list[DamageRollComponent], bool]:
    """Halve one visible attack's rolled damage and spend the defender's Reaction."""
    enabled = state.template.progression_features.uncanny_dodge
    if not enabled or not components or has_condition(state, "blinded") or not is_available(state, "reaction"):
        return components, False
    spend(state, "reaction")
    return [item.model_copy(update={"total": item.total // 2}) for item in components], True


def evasion_damage(
    state: CombatantState,
    ability: str,
    succeeded: bool,
    success_damage: str,
    total: int,
) -> int:
    """Apply Evasion only to Dexterity saves that normally deal half damage on success."""
    enabled = state.template.progression_features.evasion
    if not enabled or ability != "dexterity" or success_damage != "half":
        return total // 2 if succeeded and success_damage == "half" else total
    return 0 if succeeded else total // 2
