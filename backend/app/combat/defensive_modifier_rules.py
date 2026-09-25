from __future__ import annotations

import logging

from app.content.monster_creature_types import base_creature_type
from app.domain.models import CombatantState, CombatantTemplate
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _source_type_matches(modifier: CombatModifier, source: CombatantTemplate | None) -> bool:
    if not modifier.source_creature_types:
        return True
    source_type = base_creature_type(source.creature_type) if source is not None else None
    return source_type is not None and source_type in {item.casefold() for item in modifier.source_creature_types}


def attacks_against_disadvantage_sources(
    defender: CombatantState,
    attacker: CombatantTemplate,
) -> int:
    return sum(
        1 for item in defender.active_modifiers
        if item.kind is ModifierKind.ATTACKS_AGAINST_DISADVANTAGE
        and _source_type_matches(item, attacker)
    )


def _saving_throw_advantage_modifiers(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None = None,
) -> list[CombatModifier]:
    try:
        resolved_context = context or SavingThrowContext()
        return [
            item for item in state.active_modifiers
            if item.kind is ModifierKind.SAVING_THROW_ADVANTAGE
            and item.save_ability == ability
            and (not item.requires_magical_effect or resolved_context.magical_effect)
            and (not item.requires_spell_effect or resolved_context.spell_effect)
            and set(item.required_effect_tags).issubset(resolved_context.effect_tags)
            and (
                not item.source_creature_types
                or (
                    resolved_context.source_creature_type is not None
                    and resolved_context.source_creature_type.casefold()
                    in {value.casefold() for value in item.source_creature_types}
                )
            )
        ]
    except Exception:
        logger.exception(
            "Failed to resolve saving-throw Advantage sources for %s / %s.",
            state.template.name,
            ability,
        )
        raise


def saving_throw_advantage_sources(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None = None,
) -> int:
    return len(_saving_throw_advantage_modifiers(state, ability, context))


def saving_throw_advantage_source_names(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None = None,
) -> list[str]:
    try:
        return sorted({
            item.source_name or item.source_effect_id
            for item in _saving_throw_advantage_modifiers(state, ability, context)
        })
    except Exception:
        logger.exception(
            "Failed to identify saving-throw Advantage source names for %s / %s.",
            state.template.name,
            ability,
        )
        raise


def saving_throw_disadvantage_sources(state: CombatantState) -> int:
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE)


def consume_saving_throw_modifiers(state: CombatantState) -> list[str]:
    removed = [
        item.source_effect_id for item in state.active_modifiers
        if item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE and item.consume_on_saving_throw
    ]
    state.active_modifiers = [
        item for item in state.active_modifiers
        if not (item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE and item.consume_on_saving_throw)
    ]
    return sorted(set(removed))


def death_save_advantage_sources(state: CombatantState) -> int:
    return sum(1 for item in state.active_modifiers if item.kind is ModifierKind.DEATH_SAVE_ADVANTAGE)


def healing_is_maximized(state: CombatantState) -> bool:
    return any(item.kind is ModifierKind.HEALING_MAXIMIZE for item in state.active_modifiers)


def condition_immunity_modifier_applies(
    modifier: CombatModifier,
    condition_id: str,
    source: CombatantTemplate | None,
) -> bool:
    return (
        modifier.kind is ModifierKind.CONDITION_IMMUNITY
        and modifier.condition_id == condition_id
        and _source_type_matches(modifier, source)
    )


def targeting_save_gate(state: CombatantState) -> CombatModifier | None:
    gates = [item for item in state.active_modifiers if item.kind is ModifierKind.TARGETING_SAVE_GATE]
    return max(gates, key=lambda item: (item.save_dc or 0, item.id), default=None)


def remove_owner_attack_ending_modifiers(state: CombatantState) -> list[str]:
    removed = [item.source_effect_id for item in state.active_modifiers if item.ends_on_owner_attack]
    state.active_modifiers = [item for item in state.active_modifiers if not item.ends_on_owner_attack]
    return sorted(set(removed))
