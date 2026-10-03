from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
_PREFIX = "friendly-save-aura:"
_CONDITION_PREFIX = "friendly-condition-aura:"
_DEFENSE_PREFIX = "friendly-defense-aura:"
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _active(source: EncounterCombatant, action_id: str) -> bool:
    try:
        state = source.state
        if state.is_dead or not state.is_alive or state.current_hp <= 0 or is_incapacitated(state):
            return False
        return any(
            effect.source_id == source.combatant_id and effect.source_effect_id == action_id
            for effect in state.timed_effects
        )
    except Exception:
        logger.exception("Failed to evaluate friendly save-aura source %s.", source.combatant_id)
        raise


def _passive_active(source: EncounterCombatant, aura) -> bool:
    try:
        state = source.state
        if state.is_dead or not state.is_alive or state.current_hp <= 0:
            return False
        if aura.inactive_while_incapacitated and is_incapacitated(state):
            return False
        if aura.inactive_while_unconscious and (
            state.is_unconscious or has_condition(state, "unconscious")
        ):
            return False
        return True
    except Exception:
        logger.exception("Failed to evaluate passive friendly save-aura source %s.", source.combatant_id)
        raise


def _clear(setup: EncounterSetup) -> None:
    for member in _members(setup):
        member.state.active_modifiers = [
            item for item in member.state.active_modifiers
            if not item.id.startswith(_PREFIX)
            and not item.id.startswith(_CONDITION_PREFIX)
            and not item.id.startswith(_DEFENSE_PREFIX)
        ]


def sync_friendly_save_auras(setup: EncounterSetup) -> None:
    """Refresh active source-owned friendly save auras from live positions and state."""
    try:
        _clear(setup)
        all_members = _members(setup)
        for source in all_members:
            actions = [
                action for action in source.state.template.timed_self_buff_actions
                if action.friendly_save_advantage_aura is not None and _active(source, action.id)
            ]
            if not actions:
                continue
            allies = setup.heroes if source.side == "heroes" else setup.monsters
            for action in actions:
                aura = action.friendly_save_advantage_aura
                if aura is None:
                    continue
                for target in allies:
                    if target.state.is_dead or not target.state.is_alive:
                        continue
                    if combatant_distance(source, target) > aura.radius_ft:
                        continue
                    if aura.requires_hearing and has_condition(target.state, "deafened"):
                        continue
                    for ability in _ABILITIES:
                        for tag in aura.required_effect_tags:
                            add_modifier(target.state, CombatModifier(
                                id=f"{_PREFIX}{source.combatant_id}:{action.id}:{target.combatant_id}:{ability}:{tag}",
                                source_id=source.combatant_id,
                                source_effect_id=action.id,
                                source_name=action.name,
                                kind=ModifierKind.SAVING_THROW_ADVANTAGE,
                                save_ability=ability,
                                required_effect_tags=[tag],
                            ))

        for target in all_members:
            allies = setup.heroes if target.side == "heroes" else setup.monsters
            for source in allies:
                aura = source.state.template.progression_features.friendly_saving_throw_aura
                if aura is None or not _passive_active(source, aura):
                    continue
                if combatant_distance(source, target) > aura.radius_ft:
                    continue
                add_modifier(target.state, CombatModifier(
                    id=f"{_PREFIX}flat:{source.combatant_id}:{aura.source_id}:{target.combatant_id}",
                    source_id=source.combatant_id,
                    source_effect_id=aura.source_id,
                    source_name=aura.source_name,
                    kind=ModifierKind.SAVING_THROW_FLAT,
                    flat_bonus=aura.flat_bonus,
                    non_stacking_group=aura.non_stacking_group,
                ))

            for source in allies:
                for aura in source.state.template.progression_features.friendly_defensive_auras:
                    if not _passive_active(source, aura):
                        continue
                    active = any(
                        effect.source_id == source.combatant_id
                        and effect.source_effect_id == aura.required_source_effect_id
                        for effect in source.state.timed_effects
                    )
                    if not active or combatant_distance(source, target) > aura.radius_ft:
                        continue
                    if aura.armor_class_bonus:
                        add_modifier(target.state, CombatModifier(
                            id=f"{_DEFENSE_PREFIX}{source.combatant_id}:{aura.source_id}:{target.combatant_id}:ac",
                            source_id=source.combatant_id,
                            source_effect_id=aura.source_id,
                            source_name=aura.source_name,
                            kind=ModifierKind.ARMOR_CLASS,
                            flat_bonus=aura.armor_class_bonus,
                            non_stacking_group=aura.non_stacking_group,
                        ))
                    for ability in aura.saving_throw_abilities:
                        add_modifier(target.state, CombatModifier(
                            id=f"{_DEFENSE_PREFIX}{source.combatant_id}:{aura.source_id}:{target.combatant_id}:save:{ability}",
                            source_id=source.combatant_id,
                            source_effect_id=aura.source_id,
                            source_name=aura.source_name,
                            kind=ModifierKind.SAVING_THROW_FLAT,
                            flat_bonus=aura.saving_throw_bonus,
                            save_ability=ability,
                            non_stacking_group=aura.non_stacking_group,
                        ))

            for source in allies:
                for aura in source.state.template.progression_features.friendly_condition_immunity_auras:
                    if not _passive_active(source, aura):
                        continue
                    if combatant_distance(source, target) > aura.radius_ft:
                        continue
                    if aura.condition_id in target.state.template.condition_immunities:
                        continue
                    add_modifier(target.state, CombatModifier(
                        id=(
                            f"{_CONDITION_PREFIX}{source.combatant_id}:"
                            f"{aura.source_id}:{target.combatant_id}:{aura.condition_id}"
                        ),
                        source_id=source.combatant_id,
                        source_effect_id=aura.source_id,
                        source_name=aura.source_name,
                        kind=ModifierKind.CONDITION_IMMUNITY,
                        condition_id=aura.condition_id,
                    ))
    except Exception:
        logger.exception("Failed to synchronize friendly save auras.")
        raise
