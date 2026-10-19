"""Apply ordered hit components through the existing typed-defense/HP primitives.

A terminal monster stops at 0 HP; a dying character continues through later
damage components, which use the existing damage-at-zero/death-save rules.
"""
from __future__ import annotations

import logging

from app.combat.damage_defenses import resolve_damage_amount
from app.combat.zero_hp import apply_damage
from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_ordered_hit_damage(
    target: CombatantState,
    components: list[DamageRollComponent],
    *,
    critical: bool,
    dice,
    affected_states,
    setup,
    ignored_resistance_types: set[DamageType] | None,
) -> tuple[int, list[DamageRollComponent], str | None]:
    """Stop when a monster reaches terminal 0 HP or any combatant is dead.

    The shared zero-HP resolver handles a character's subsequent damage-at-zero
    failures, and honors source-defined survival/replacement effects.
    """
    try:
        processed: list[DamageRollComponent] = []
        applied_total = 0
        outcome: str | None = None
        for component in components:
            if target.is_dead or (target.template.kind == "monster" and target.current_hp <= 0):
                break
            applied, healed, absorption_source = resolve_damage_amount(
                component.total,
                component.damage_type,
                target,
                source_qualifiers=set(component.source_qualifiers),
                ignored_resistance_types=ignored_resistance_types,
            )
            resolved = component.model_copy(update={
                "applied_total": applied,
                "absorbed_healing": healed,
                "absorption_source_name": absorption_source,
            })
            processed.append(resolved)
            applied_total += applied
            if applied > 0:
                outcome = apply_damage(
                    target, applied, critical=critical,
                    damage_types={component.damage_type},
                    dice=dice, affected_states=affected_states, setup=setup,
                    damage_components=[resolved],
                )
        return applied_total, processed, outcome
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ordered attack damage failed for %s.", target.template.name)
        raise RuntimeError("Ordered hit damage could not be resolved.") from exc
