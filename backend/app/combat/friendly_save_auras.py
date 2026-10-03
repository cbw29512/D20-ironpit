from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
_PREFIX = "friendly-save-aura:"
_COVER_PREFIX = "friendly-cover-aura:"
_CONDITION_PREFIX = "friendly-condition-aura:"
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
            if not item.id.startswith(_PREFIX) and not item.id.startswith(_COVER_PREFIX)
            and not item.id.startswith(_CONDITION_PREFIX)
        ]


def sync_friendly_save_auras(setup: EncounterSetup) -> None:
    """Refresh active source-owned friendly save auras from live positions and state."""
    try:
        _clear(setup)
        all_members = _members(setup)
        for source in all_members:
            actions = [
                action for action in source.state.template.timed_self_buff_actions
                if (
                    action.friendly_save_advantage_aura is not None
                    or action.friendly_cover_aura is not None
                )
                and _active(source, action.id)
            ]
            if not actions:
                continue
            allies = setup.heroes if source.side == "heroes" else setup.monsters
            for action in actions:
                save_aura = action.friendly_save_advantage_aura
                cover_aura = action.friendly_cover_aura
                for target in allies:
                    if target.state.is_dead or not target.state.is_alive:
                        continue
                    if save_aura is not None and combatant_distance(source, target) <= save_aura.radius_ft:
                        if not (save_aura.requires_hearing and has_condition(target.state, "deafened")):
                            for ability in _ABILITIES:
                                for tag in save_aura.required_effect_tags:
                                    add_modifier(target.state, CombatModifier(
                                        id=f"{_PREFIX}{source.combatant_id}:{action.id}:{target.combatant_id}:{ability}:{tag}",
                                        source_id=source.combatant_id,
                                        source_effect_id=action.id,
                                        source_name=action.name,
                                        kind=ModifierKind.SAVING_THROW_ADVANTAGE,
                                        save_ability=ability,
                                        required_effect_tags=[tag],
                                    ))
                    if cover_aura is not None and combatant_distance(source, target) <= cover_aura.radius_ft:
                        add_modifier(target.state, CombatModifier(
                            id=f"{_COVER_PREFIX}{source.combatant_id}:{action.id}:{target.combatant_id}:ac",
                            source_id=source.combatant_id,
                            source_effect_id=action.id,
                            source_name=action.name,
                            kind=ModifierKind.COVER_ARMOR_CLASS,
                            flat_bonus=cover_aura.cover_bonus,
                        ))
                        add_modifier(target.state, CombatModifier(
                            id=f"{_COVER_PREFIX}{source.combatant_id}:{action.id}:{target.combatant_id}:dex",
                            source_id=source.combatant_id,
                            source_effect_id=action.id,
                            source_name=action.name,
                            kind=ModifierKind.COVER_SAVING_THROW_FLAT,
                            flat_bonus=cover_aura.cover_bonus,
                            save_ability="dexterity",
                        ))

        for target in all_members:
            allies = setup.heroes if target.side == "heroes" else setup.monsters
            candidates = []
            for source in allies:
                aura = source.state.template.progression_features.friendly_saving_throw_aura
                if aura is None or not _passive_active(source, aura):
                    continue
                if combatant_distance(source, target) > aura.radius_ft:
                    continue
                candidates.append((aura.flat_bonus, source.combatant_id, source, aura))
            if candidates:
                _, _, source, aura = max(candidates, key=lambda item: (item[0], item[1]))
                add_modifier(target.state, CombatModifier(
                    id=f"{_PREFIX}flat:{source.combatant_id}:{aura.source_id}:{target.combatant_id}",
                    source_id=source.combatant_id,
                    source_effect_id=aura.source_id,
                    source_name=aura.source_name,
                    kind=ModifierKind.SAVING_THROW_FLAT,
                    flat_bonus=aura.flat_bonus,
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
