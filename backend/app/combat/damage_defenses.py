from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.damage_sources import DamageDefenseKind, DamageSourceQualifier

logger = logging.getLogger(__name__)


def _active_timed_resistances(target: CombatantState) -> set[DamageType]:
    """Return typed resistances owned by currently active timed effects."""
    try:
        return {
            damage_type
            for effect in target.timed_effects
            for damage_type in effect.owned_damage_resistances
        }
    except Exception as exc:
        logger.exception("Timed resistance lookup failed for %s.", target.template.name)
        raise RuntimeError("Timed resistances could not be resolved.") from exc


def _matching_conditional_defenses(
    target: CombatantState,
    damage_type: DamageType,
    source_qualifiers: set[DamageSourceQualifier],
) -> set[DamageDefenseKind]:
    try:
        matched: set[DamageDefenseKind] = set()
        for rule in target.template.conditional_damage_defenses:
            if damage_type not in rule.damage_types:
                continue
            required = set(rule.required_source_qualifiers)
            forbidden = set(rule.forbidden_source_qualifiers)
            if not required.issubset(source_qualifiers) or forbidden.intersection(source_qualifiers):
                continue
            matched.add(rule.kind)
        return matched
    except Exception as exc:
        logger.exception("Conditional damage-defense matching failed for %s.", target.template.name)
        raise RuntimeError("Conditional damage defenses could not be matched.") from exc


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
    source_qualifiers: set[DamageSourceQualifier] | None = None,
) -> int:
    """Apply immunity/resistance and, when allowed, vulnerability to one damage type."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        template = target.template
        qualifiers = source_qualifiers or set()
        conditional = _matching_conditional_defenses(target, damage_type, qualifiers)
        if damage_type in template.damage_immunities or DamageDefenseKind.IMMUNITY in conditional:
            return 0

        adjusted = amount
        resistances = {
            *template.damage_resistances,
            *target.temporary_damage_resistances,
            *_active_timed_resistances(target),
        }
        if (
            damage_type in resistances
            or DamageDefenseKind.RESISTANCE in conditional
            or has_condition(target, "petrified")
        ):
            adjusted //= 2
        if allow_vulnerability and (
            damage_type in template.damage_vulnerabilities
            or DamageDefenseKind.VULNERABILITY in conditional
        ):
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
                source_qualifiers=set(component.source_qualifiers),
            )
            adjusted_components.append(component.model_copy(update={"applied_total": applied}))
            applied_total += applied
        return applied_total, adjusted_components
    except Exception as exc:
        logger.exception("Typed damage defenses failed for %s.", target.template.name)
        raise RuntimeError("Typed damage defenses could not be applied.") from exc