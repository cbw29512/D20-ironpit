"""Apply fight-local weapon corrosion to the base damage roll, never its riders."""
from __future__ import annotations

from app.combat.weapon_corrosion import (
    apply_weapon_corrosion_damage_penalty, corrosion_penalty,
)
from app.domain.models import CombatantState, DamageRollComponent


def corrosion_adjusted_weapon_component(
    attacker: CombatantState, weapon_id: str, component: DamageRollComponent,
) -> DamageRollComponent:
    """Keep immutable attack dice; source type and bonus rider rolls unchanged."""
    penalty = corrosion_penalty(attacker, weapon_id)
    if penalty == 0:
        return component
    value = apply_weapon_corrosion_damage_penalty(
        attacker, weapon_id, max(0, component.total),
    )
    return component.model_copy(update={
        "total": value,
        "modifier": component.modifier + penalty,
        "notation": f"{component.notation} [corrosion {penalty}]",
    })
