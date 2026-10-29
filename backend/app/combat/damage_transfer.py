from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _split_components(
    components: list[DamageRollComponent] | None,
    total: int,
    source_total: int,
) -> tuple[list[DamageRollComponent] | None, list[DamageRollComponent] | None]:
    if not components:
        return components, components
    applied = [max(0, int(item.applied_total or 0)) for item in components]
    source_parts = [value * source_total // total for value in applied]
    unassigned = min(source_total - sum(source_parts), sum(applied) - sum(source_parts))
    order = sorted(
        range(len(applied)),
        key=lambda index: (applied[index] * source_total % total, -index),
        reverse=True,
    )
    for index in order:
        if unassigned <= 0:
            break
        if source_parts[index] < applied[index]:
            source_parts[index] += 1
            unassigned -= 1
    source = [
        item.model_copy(update={"applied_total": part})
        for item, part in zip(components, source_parts)
    ]
    target = [
        item.model_copy(update={"applied_total": value - part})
        for item, value, part in zip(components, applied, source_parts)
    ]
    return source, target


def resolve_damage_transfer_for_state(
    source_state: CombatantState,
    amount: int,
    setup: EncounterSetup | None,
    dice,
    damage_types: set[DamageType],
    damage_components: list[DamageRollComponent] | None,
) -> tuple[int, list[DamageRollComponent] | None]:
    """Return source damage/components after transferring the other half once."""
    try:
        rule = source_state.template.damage_transfer
        if rule is None or amount <= 0:
            return amount, damage_components
        if rule.relation != "source_grapples_target" or rule.source_rounding != "down":
            raise ValueError("Unsupported Damage Transfer source parameters.")
        if setup is None:
            raise ValueError("Damage Transfer requires encounter setup.")
        source = next((item for item in _members(setup) if item.state is source_state), None)
        if source is None:
            raise ValueError("Damage Transfer source is absent from encounter setup.")
        targets = [
            item for item in _members(setup)
            if item.state.is_alive and not item.state.is_dead
            and any(link.source_id == source.combatant_id for link in item.state.grapple_sources)
        ]
        if not targets:
            return amount, damage_components
        if len(targets) != 1:
            raise ValueError("Damage Transfer requires exactly one attached/grappled target.")
        source_keeps = amount // 2
        target_takes = amount - source_keeps
        source_components, target_components = _split_components(
            damage_components, amount, source_keeps,
        )
        from app.combat.zero_hp import apply_damage

        apply_damage(
            targets[0].state,
            target_takes,
            damage_types=damage_types,
            dice=dice,
            affected_states=[item.state for item in _members(setup)],
            setup=setup,
            damage_components=target_components,
            allow_damage_transfer=rule.transferred_damage_retriggers,
        )
        return source_keeps, source_components
    except Exception:
        logger.exception("Failed to resolve Damage Transfer for %s.", source_state.template.name)
        raise
