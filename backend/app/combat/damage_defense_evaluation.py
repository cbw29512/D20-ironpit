from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.damage_sources import DamageDefenseKind, DamageSourceQualifier
from app.domain.models import CombatantState, DamageType

logger = logging.getLogger(__name__)


def matching_absorption(target: CombatantState, damage_type: DamageType):
    """Return the one typed absorption rule that applies, if any."""
    try:
        matches = [
            rule for rule in target.template.damage_absorptions
            if rule.damage_type == damage_type
        ]
        if len(matches) > 1:
            raise ValueError(
                f"{target.template.name} has multiple absorption rules for {damage_type.value}."
            )
        return matches[0] if matches else None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage absorption lookup failed for %s.", target.template.name)
        raise RuntimeError("Damage absorption could not be resolved.") from exc


def active_timed_resistances(target: CombatantState) -> set[DamageType]:
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


def matching_conditional_defenses(
    target: CombatantState,
    damage_type: DamageType,
    source_qualifiers: set[DamageSourceQualifier],
) -> set[DamageDefenseKind]:
    """Return conditional defense kinds whose source qualifiers match this component."""
    try:
        matched: set[DamageDefenseKind] = set()
        for rule in [
            *target.template.conditional_damage_defenses,
            *target.active_conditional_damage_defenses,
        ]:
            if damage_type not in rule.damage_types:
                continue
            required = set(rule.required_source_qualifiers)
            forbidden = set(rule.forbidden_source_qualifiers)
            if not required.issubset(source_qualifiers) or forbidden.intersection(source_qualifiers):
                continue
            matched.add(rule.kind)
        return matched
    except Exception as exc:
        logger.exception("Conditional damage defense lookup failed for %s.", target.template.name)
        raise RuntimeError("Conditional damage defenses could not be resolved.") from exc


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
    source_qualifiers: set[DamageSourceQualifier] | None = None,
    ignored_resistance_types: set[DamageType] | None = None,
) -> int:
    """Purely estimate one typed component after defenses; never mutate combat state."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        template = target.template
        conditional = matching_conditional_defenses(target, damage_type, source_qualifiers or set())
        if (
            matching_absorption(target, damage_type) is not None
            or damage_type in template.damage_immunities
            or damage_type in target.zone_damage_immunities
            or DamageDefenseKind.IMMUNITY in conditional
        ):
            return 0

        adjusted = amount
        resistances = {
            *template.damage_resistances,
            *target.temporary_damage_resistances,
            *active_timed_resistances(target),
        }
        ignores_resistance = damage_type in (ignored_resistance_types or set())
        if not ignores_resistance and (
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
