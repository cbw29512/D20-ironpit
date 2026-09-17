from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState, DamageRollComponent


def can_uncanny_dodge(attacker: CombatantState, defender: CombatantState) -> bool:
    """Return whether the defender can see this attacker and spend its Reaction."""
    return bool(
        defender.template.progression_features.uncanny_dodge
        and not has_condition(defender, "blinded")
        and not has_condition(attacker, "invisible")
        and is_available(defender, "reaction")
    )


def apply_uncanny_dodge(
    attacker: CombatantState,
    defender: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[list[DamageRollComponent], bool]:
    """Halve one visible attack's rolled damage and spend the defender's Reaction."""
    if not components or not can_uncanny_dodge(attacker, defender):
        return components, False
    spend(defender, "reaction")
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
