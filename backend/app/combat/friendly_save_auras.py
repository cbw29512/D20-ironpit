from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition, is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
_PREFIX = "friendly-save-aura:"
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


def _clear(setup: EncounterSetup) -> None:
    for member in _members(setup):
        member.state.active_modifiers = [
            item for item in member.state.active_modifiers
            if not item.id.startswith(_PREFIX)
        ]


def sync_friendly_save_auras(setup: EncounterSetup) -> None:
    """Refresh active source-owned friendly save auras from live positions and state."""
    try:
        _clear(setup)
        for source in _members(setup):
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
    except Exception:
        logger.exception("Failed to synchronize friendly save auras.")
        raise
