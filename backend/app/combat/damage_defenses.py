from __future__ import annotations

import logging

from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
) -> int:
    """Apply SRD 5.2.1 immunity, resistance, then vulnerability to one damage type."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        template = target.template
        if damage_type in template.damage_immunities:
            return 0

        adjusted = amount
        resistances = {
            *template.damage_resistances,
            *target.temporary_damage_resistances,
        }
        if damage_type in resistances:
            adjusted //= 2
        if damage_type in template.damage_vulnerabilities:
            adjusted *= 2
        return adjusted
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage defense resolution failed for %s.", target.template.name)
        raise RuntimeError("Damage defenses could not be resolved.") from exc


def apply_damage_defenses(
    target: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[int, list[DamageRollComponent]]:
    """Apply defenses per typed component and return the total damage actually taken."""
    try:
        adjusted_components: list[DamageRollComponent] = []
        applied_total = 0
        for component in components:
            applied = adjusted_damage_amount(
                component.total,
                component.damage_type,
                target,
            )
            adjusted_components.append(component.model_copy(update={"applied_total": applied}))
            applied_total += applied
        return applied_total, adjusted_components
    except Exception as exc:
        logger.exception("Typed damage defenses failed for %s.", target.template.name)
        raise RuntimeError("Typed damage defenses could not be applied.") from exc
