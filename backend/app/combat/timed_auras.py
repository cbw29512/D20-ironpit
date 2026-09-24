from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage import fixed_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.content.monster_creature_types import base_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.timed_auras import TimedAuraAction

logger = logging.getLogger(__name__)
_AURA_EFFECT_ID = "timed-aura"


def _active(state, action: TimedAuraAction) -> bool:
    return any(
        effect.effect_id == _AURA_EFFECT_ID and effect.source_effect_id == action.id
        for effect in state.timed_effects
    )


def choose_timed_aura_action(member: EncounterCombatant) -> TimedAuraAction | None:
    try:
        choices = []
        for action in member.state.template.timed_aura_actions:
            resource = next((item for item in member.state.resources if item.id == action.resource_id), None)
            if is_available(member.state, action.action_cost) and resource and resource.current_uses >= action.resource_cost and not _active(member.state, action):
                choices.append(action)
        return max(choices, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Timed aura choice failed for %s.", member.combatant_id)
        raise RuntimeError("Timed aura choice could not be resolved.") from exc


def resolve_timed_aura_activation(
    sequence: int, round_number: int, member: EncounterCombatant, action: TimedAuraAction,
) -> BattleEvent:
    try:
        resource = next((item for item in member.state.resources if item.id == action.resource_id), None)
        if not is_available(member.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if resource is None or resource.current_uses < action.resource_cost:
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        spend(member.state, action.action_cost)
        resource.current_uses -= action.resource_cost
        apply_timed_condition(
            member.state, _AURA_EFFECT_ID, member.combatant_id,
            source_effect_id=action.id, applied_round=round_number,
            expires_round=round_number + action.duration_rounds,
            expiry_timing="source_turn_start", use_default_poison_recovery=False,
        )
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=member.combatant_id, actor_name=member.state.template.name,
            target_id=member.combatant_id, target_name=member.state.template.name,
            feature_id=action.id, resource_remaining=resource.current_uses,
            animation=action.animation, description=f"{member.state.template.name} uses {action.name}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Timed aura activation failed for %s.", member.combatant_id)
        raise RuntimeError("Timed aura activation could not be resolved.") from exc


def _matching_save_auras(state, ability: str, context: SavingThrowContext | None) -> list[TimedAuraAction]:
    resolved = context or SavingThrowContext()
    source_type = base_creature_type(resolved.source_creature_type) if resolved.source_creature_type else None
    return [
        action for action in state.template.timed_aura_actions
        if _active(state, action)
        and ability in action.saving_throw_advantage_abilities
        and (not action.saving_throw_advantage_requires_spell or resolved.source_is_spell)
        and (
            not action.saving_throw_advantage_source_creature_types
            or source_type in {item.casefold() for item in action.saving_throw_advantage_source_creature_types}
        )
    ]


def timed_aura_saving_throw_advantage_sources(state, ability: str, context: SavingThrowContext | None = None) -> int:
    try:
        return len(_matching_save_auras(state, ability, context))
    except Exception as exc:
        logger.exception("Timed aura save-Advantage lookup failed for %s.", state.template.name)
        raise RuntimeError("Timed aura save Advantage could not be resolved.") from exc


def timed_aura_saving_throw_advantage_source_names(state, ability: str, context: SavingThrowContext | None = None) -> list[str]:
    try:
        return sorted({action.name for action in _matching_save_auras(state, ability, context)})
    except Exception as exc:
        logger.exception("Timed aura save-Advantage source lookup failed for %s.", state.template.name)
        raise RuntimeError("Timed aura save-Advantage sources could not be resolved.") from exc


def resolve_enemy_start_turn_auras(
    sequence: int, round_number: int, target: EncounterCombatant, setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    try:
        enemies = setup.monsters if target.side == "heroes" else setup.heroes
        affected_states = [item.state for item in [*setup.heroes, *setup.monsters]]
        events: list[BattleEvent] = []
        for source in enemies:
            for action in source.state.template.timed_aura_actions:
                if not _active(source.state, action) or action.start_turn_fixed_damage <= 0:
                    continue
                if combatant_distance(source, target) > action.radius_ft:
                    continue
                component = fixed_damage_component(action.name, action.start_turn_fixed_damage, DamageType(action.damage_type))
                applied, components = apply_damage_defenses(target.state, [component])
                hp_before = target.state.current_hp
                if applied:
                    apply_damage(target.state, applied, damage_types={DamageType(action.damage_type)}, affected_states=affected_states)
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="damage",
                    actor_id=source.combatant_id, actor_name=source.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    damage_components=components, hp_before=hp_before, hp_after=target.state.current_hp,
                    is_dead=target.state.is_dead, feature_id=action.id, animation=action.animation,
                    description=f"{target.state.template.name} takes {applied} {action.damage_type} damage from {action.name}.",
                ))
                sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Timed aura start-turn resolution failed for %s.", target.combatant_id)
        raise RuntimeError("Timed aura start-turn effects could not be resolved.") from exc
