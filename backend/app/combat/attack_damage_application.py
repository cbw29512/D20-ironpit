from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.projectile_catch import resolve_projectile_catch
from app.combat.zero_hp import apply_damage
from app.domain.models import CombatantState, WeaponAttack


def apply_attack_damage(
    defender: CombatantState,
    attack: WeaponAttack,
    rolled_components,
    dice,
    *,
    critical: bool,
    affected_states: list[CombatantState] | None,
):
    """Apply defenses, reaction interception, then HP damage in canonical order."""
    _, components = apply_damage_defenses(defender, rolled_components, attack=attack)
    components, reaction_roll, reaction_succeeded = resolve_projectile_catch(defender, attack, components, dice)
    total = sum(part.applied_total or 0 for part in components)
    types = {part.damage_type for part in components if (part.applied_total or 0) > 0}
    outcome = apply_damage(defender, total, critical=critical, damage_types=types, dice=dice, affected_states=affected_states)
    return total, components, outcome, reaction_roll, reaction_succeeded
