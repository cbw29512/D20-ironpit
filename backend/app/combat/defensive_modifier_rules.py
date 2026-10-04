from __future__ import annotations

import logging

from app.combat.defensive_modifier_lifecycle import consume_saving_throw_modifiers, remove_owner_attack_ending_modifiers

from app.content.monster_creature_types import base_creature_type
from app.domain.models import CombatantState, CombatantTemplate
from app.domain.modifiers import CombatModifier, ModifierKind
from app.combat.modifier_stack import d20_test_advantage_sources
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)

def _source_type_matches(modifier: CombatModifier, source: CombatantTemplate | None) -> bool:
    if not modifier.source_creature_types:
        return True
    source_type = base_creature_type(source.creature_type) if source is not None else None
    return source_type is not None and source_type in {item.casefold() for item in modifier.source_creature_types}

def _attacker_sense_bypasses(
    modifier: CombatModifier,
    attacker: CombatantTemplate,
    distance_ft: int | None,
) -> bool:
    if distance_ft is None:
        return False
    ranges = {
        "blindsight": attacker.blindsight_ft,
        "truesight": attacker.truesight_ft,
    }
    return any(ranges[sense] >= distance_ft for sense in modifier.bypass_attacker_senses)

def attacks_against_disadvantage_sources(
    defender: CombatantState,
    attacker: CombatantTemplate,
    distance_ft: int | None = None,
) -> int:
    return sum(
        1 for item in defender.active_modifiers
        if item.kind is ModifierKind.ATTACKS_AGAINST_DISADVANTAGE
        and _source_type_matches(item, attacker)
        and not _attacker_sense_bypasses(item, attacker, distance_ft)
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
    return len(_saving_throw_advantage_modifiers(state, ability, context)) + d20_test_advantage_sources(state)


def saving_throw_advantage_source_names(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None = None,
) -> list[str]:
    try:
        contextual = _saving_throw_advantage_modifiers(state, ability, context)
        universal = [
            item for item in state.active_modifiers
            if item.kind is ModifierKind.D20_TEST_ADVANTAGE
        ]
        return sorted({
            item.source_name or item.source_effect_id
            for item in [*contextual, *universal]
        })
    except Exception:
        logger.exception(
            "Failed to identify saving-throw Advantage source names for %s / %s.",
            state.template.name,
            ability,
        )
        raise


def saving_throw_disadvantage_sources(state: CombatantState, ability: str | None = None) -> int:
    return sum(
        1 for item in state.active_modifiers
        if item.kind is ModifierKind.SAVING_THROW_DISADVANTAGE
        and (ability is None or item.save_ability is None or item.save_ability == ability)
    )



def death_save_advantage_sources(state: CombatantState) -> int:
    return sum(
        1 for item in state.active_modifiers
        if item.kind in {ModifierKind.DEATH_SAVE_ADVANTAGE, ModifierKind.D20_TEST_ADVANTAGE}
    )


def healing_is_maximized(state: CombatantState) -> bool:
    return any(item.kind is ModifierKind.HEALING_MAXIMIZE for item in state.active_modifiers)


def condition_immunity_modifier_applies(
    modifier: CombatModifier,
    state: CombatantState,
    condition_id: str,
    source: CombatantTemplate | None,
) -> bool:
    try:
        return (
            modifier.kind is ModifierKind.CONDITION_IMMUNITY
            and modifier.condition_id == condition_id
            and _source_type_matches(modifier, source)
            and set(modifier.required_active_effect_ids).issubset(state.active_effect_ids)
        )
    except Exception:
        logger.exception(
            "Failed to resolve condition-immunity modifier %s for %s.",
            modifier.id,
            state.template.name,
        )
        raise


def targeting_save_gate(
    state: CombatantState,
    source: CombatantTemplate | None = None,
) -> CombatModifier | None:
    gates = [
        item for item in state.active_modifiers
        if item.kind is ModifierKind.TARGETING_SAVE_GATE
        and _source_type_matches(item, source)
    ]
    return max(gates, key=lambda item: (item.save_dc or 0, item.id), default=None)
