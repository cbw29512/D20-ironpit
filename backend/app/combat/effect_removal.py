from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.dice import DiceProvider
from app.combat.effect_removal_targets import TrackedSpellEffect, TaggedConditionTarget, removal_targets
from app.combat.effect_removal_multi import resolve_target_spell_effects, apply_target_spell_effects
from app.combat.effect_removal_slot_choice import choose_effect_removal_slot
from app.combat.effect_tag_conditions import apply_tagged_condition
from app.combat.modifier_stack import remove_source_modifiers
from app.combat.rolls import roll_d20
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.domain.effect_removal import EffectRemovalAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def action_available(remover, action, turn_key):
    if not is_available(remover.state, action.action_cost):
        return False
    if action.expends_spell_slot and not slot_spell_available(remover.state, turn_key):
        return False
    if action.upcast_slot_level:
        resource_id, cast_level = choose_effect_removal_slot(remover, action, turn_key)
        return resource_id is not None and cast_level is not None
    resource = next((item for item in remover.state.resources if item.id == action.resource_id), None)
    return action.resource_id is None or (resource is not None and resource.current_uses >= action.resource_cost)


def choose_effect_removal_action(
    remover: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[EffectRemovalAction, TrackedSpellEffect | TaggedConditionTarget] | None:
    for action in remover.state.template.effect_removal_actions:
        if not action_available(remover, action, turn_key):
            continue
        effects = removal_targets(remover, setup, action)
        # Automated dispelling should only remove enemy-owned magic:
        # an enemy's ward or an enemy spell affecting our allies.
        # The legal resolver remains unchanged for deliberate/manual removal.
        for effect in effects:
            if isinstance(effect, TaggedConditionTarget) or effect.source.side != remover.side:
                return action, effect
    return None


def resolve_effect_removal(
    sequence: int,
    round_number: int,
    remover: EncounterCombatant,
    setup: EncounterSetup,
    action: EffectRemovalAction,
    effect: TrackedSpellEffect | TaggedConditionTarget,
    dice: DiceProvider,
    turn_key: str,
) -> BattleEvent:
    try:
        if not action_available(remover, action, turn_key):
            raise ValueError("Effect-removal action or resource is no longer available.")
        if effect not in removal_targets(remover, setup, action):
            raise ValueError("Tracked spell effect is no longer a legal removal target.")
        # Determine the actual cast slot before consuming resources. Its
        # level controls the automatic-removal threshold for THIS cast.
        target_levels = (
            [item.spell_level for item in removal_targets(remover, setup, action)
             if isinstance(item, TrackedSpellEffect)
             and item.target.combatant_id == effect.target.combatant_id]
            if action.upcast_slot_level else []
        )
        slot_id, cast_level = choose_effect_removal_slot(
            remover, action, turn_key, target_levels,
        )
        if action.upcast_slot_level and slot_id is None:
            raise ValueError("No legal spell slot remains for upcast effect removal.")
        resolved_action = (
            action.model_copy(update={"auto_remove_max_level":cast_level})
            if action.upcast_slot_level else action
        )
        # Resolve the entire selected creature's spell set as one cast.
        # Validate higher-level dice/scores before spending the Action or slot.
        candidates = (
            resolve_target_spell_effects(
                remover, setup, resolved_action, effect.target, dice, round_number,
            )
            if action.remove_all_target_spells and isinstance(effect, TrackedSpellEffect)
            else None
        )
        spend(remover.state, action.action_cost)
        remaining = None
        resource_id = slot_id if action.upcast_slot_level else action.resource_id
        if resource_id is not None:
            resource = next(item for item in remover.state.resources if item.id == resource_id)
            if action.expends_spell_slot:
                mark_slot_spell_cast(remover.state, turn_key)
            resource.current_uses -= action.resource_cost
            remaining = resource.current_uses
        if isinstance(effect, TaggedConditionTarget):
            return apply_tagged_condition(sequence, round_number, remover, setup, action, effect, remaining)
        if candidates is not None:
            removed, first_check, first_dc, first_success, audit, summary = apply_target_spell_effects(
                remover, setup, resolved_action, effect.target, candidates, dice, round_number,
            )
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=remover.combatant_id, actor_name=remover.state.template.name,
                target_id=effect.target.combatant_id,
                target_name=effect.target.state.template.name,
                feature_id=action.id, resource_remaining=remaining,
                removed_condition_ids=removed, animation=action.animation,
                ability_check_roll=first_check, check_ability=action.casting_ability
                if first_check is not None else None,
                check_dc=first_dc, check_succeeded=first_success,
                audit=audit,
                description=(
                    f"{remover.state.template.name} uses {action.name} on "
                    f"{effect.target.state.template.name}: {summary}."
                ),
            )
        check = None
        succeeded = True
        dc = None
        if effect.spell_level > resolved_action.auto_remove_max_level:
            scores = remover.state.template.ability_scores
            if scores is None:
                raise ValueError("Effect-removal ability check requires certified ability scores.")
            dc = 10 + effect.spell_level
            check = roll_d20(
                dice,
                scores.modifier(action.casting_ability),
                ability_check_roll_mode(remover.state),
            )
            check, succeeded = resolve_ability_check_outcome(
                remover.state,
                action.casting_ability,
                check,
                dc,
                dice=dice,
                round_number=round_number,
                encounter_roller=remover,
                setup=setup,
            )
        if succeeded:
            remove_source_modifiers(
                [effect.target.state], effect.source.combatant_id, effect.effect_id,
            )
            effect.target.state.active_buff_effect_ids = [
                item for item in effect.target.state.active_buff_effect_ids if item != effect.effect_id
            ]
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=remover.combatant_id, actor_name=remover.state.template.name,
            target_id=effect.target.combatant_id, target_name=effect.target.state.template.name,
            ability_check_roll=check, check_ability=action.casting_ability,
            check_dc=dc, check_succeeded=succeeded if check is not None else None,
            feature_id=action.id, resource_remaining=remaining,
            removed_condition_ids=[effect.effect_id] if succeeded else [],
            animation=action.animation,
            description=(
                f"{remover.state.template.name} uses {action.name} on {effect.effect_id}: "
                f"{'effect ends' if succeeded else 'ability check fails'}."
            ),
        )
    except ValueError:
        logger.exception("Invalid effect removal for %s using %s.", remover.combatant_id, action.id)
        raise
    except Exception as exc:
        logger.exception("Effect removal failed for %s.", remover.combatant_id)
        raise RuntimeError("Tracked spell effect removal could not be resolved.") from exc
