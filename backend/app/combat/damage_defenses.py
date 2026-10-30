from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.damage_absorption import absorb_typed_damage
from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
) -> int:
    """Apply immunity/resistance and, when allowed, vulnerability to one damage type."""
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
        if damage_type in resistances or has_condition(target, "petrified"):
            adjusted //= 2
        if allow_vulnerability and damage_type in template.damage_vulnerabilities:
            adjusted *= 2
        return adjusted
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage defense resolution failed for %s.", target.template.name)
        raise RuntimeError("Damage defenses could not be resolved.") from exc


def resolve_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
) -> tuple[int, int]:
    """Resolve actual typed damage, including damage-to-healing replacement."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if damage_type in target.template.damage_absorption_types:
            before = target.current_hp
            absorb_typed_damage(target, amount, damage_type)
            return 0, target.current_hp - before
        return adjusted_damage_amount(
            amount, damage_type, target, allow_vulnerability=allow_vulnerability,
        ), 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage amount resolution failed for %s.", target.template.name)
        raise RuntimeError("Damage amount could not be resolved.") from exc


def apply_damage_defenses(
    target: CombatantState,
    components: list[DamageRollComponent],
) -> tuple[int, list[DamageRollComponent]]:
    """Apply defenses per typed component and return the total damage actually taken."""
    try:
        adjusted_components: list[DamageRollComponent] = []
        applied_total = 0
        for component in components:
            applied, _ = resolve_damage_amount(
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
