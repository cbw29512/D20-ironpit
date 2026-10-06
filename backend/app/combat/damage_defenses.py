from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.damage_defense_evaluation import (
    active_timed_resistances,
    adjusted_damage_amount,
    matching_absorption,
    matching_conditional_defenses,
)
from app.combat.incoming_damage_resistance import apply_incoming_damage_type_resistance_amount
from app.combat.zero_hp import restore_hit_points
from app.domain.damage_sources import DamageDefenseKind, DamageSourceQualifier
from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
    source_qualifiers: set[DamageSourceQualifier] | None = None,
    ignored_resistance_types: set[DamageType] | None = None,
) -> tuple[int, int, str | None]:
    """Resolve one actual typed component, including Reactions and damage-to-healing replacement."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        absorption = matching_absorption(target, damage_type)
        if absorption is not None:
            if amount == 0:
                return 0, 0, absorption.source_name
            healed = restore_hit_points(target, amount)
            return 0, healed, absorption.source_name

        kwargs = {
            "allow_vulnerability": allow_vulnerability,
            "source_qualifiers": source_qualifiers,
            "ignored_resistance_types": ignored_resistance_types,
        }
        before_reaction = adjusted_damage_amount(amount, damage_type, target, **kwargs)
        if before_reaction <= 0:
            return before_reaction, 0, None

        conditional = matching_conditional_defenses(target, damage_type, source_qualifiers or set())
        resistance_ignored = damage_type in (ignored_resistance_types or set())
        already_resisted = (
            damage_type in target.template.damage_resistances
            or damage_type in target.temporary_damage_resistances
            or damage_type in active_timed_resistances(target)
            or DamageDefenseKind.RESISTANCE in conditional
            or has_condition(target, "petrified")
        )
        if not resistance_ignored and not already_resisted:
            apply_incoming_damage_type_resistance_amount(target, amount, damage_type)
        applied = adjusted_damage_amount(amount, damage_type, target, **kwargs)
        return applied, 0, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage amount resolution failed for %s.", target.template.name)
        raise RuntimeError("Damage amount could not be resolved.") from exc


def apply_damage_defenses(
    target: CombatantState,
    components: list[DamageRollComponent],
    *,
    ignored_resistance_types: set[DamageType] | None = None,
) -> tuple[int, list[DamageRollComponent]]:
    """Resolve actual typed components and return total damage actually taken."""
    try:
        adjusted_components: list[DamageRollComponent] = []
        applied_total = 0
        for component in components:
            applied, healed, absorption_source = resolve_damage_amount(
                component.total,
                component.damage_type,
                target,
                source_qualifiers=set(component.source_qualifiers),
                ignored_resistance_types=ignored_resistance_types,
            )
            adjusted_components.append(component.model_copy(update={
                "applied_total": applied,
                "absorbed_healing": healed,
                "absorption_source_name": absorption_source,
            }))
            applied_total += applied
        return applied_total, adjusted_components
    except Exception as exc:
        logger.exception("Typed damage defenses failed for %s.", target.template.name)
        raise RuntimeError("Typed damage defenses could not be applied.") from exc
