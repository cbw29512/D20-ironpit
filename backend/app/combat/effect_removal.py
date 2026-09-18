from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import remove_source_modifiers
from app.combat.rolls import roll_d20
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.domain.effect_removal import EffectRemovalAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrackedSpellEffect:
    target: EncounterCombatant
    source: EncounterCombatant
    effect_id: str
    spell_level: int


def _spell_level(source: EncounterCombatant, effect_id: str) -> int | None:
    template = source.state.template
    spells = [
        *template.defensive_spell_actions,
        *template.spell_save_actions,
        *template.spell_attack_actions,
    ]
    spell = next((item for item in spells if item.id == effect_id), None)
    return spell.level if spell is not None else None


def _target_allowed(
    remover: EncounterCombatant,
    target: EncounterCombatant,
    action: EffectRemovalAction,
) -> bool:
    if target.state.is_dead or not target.state.is_alive:
        return False
    same_side = target.side == remover.side
    if action.target_mode == "enemy" and same_side:
        return False
    if action.target_mode == "ally" and (not same_side or target.combatant_id == remover.combatant_id):
        return False
    if action.target_mode == "self_or_ally" and not same_side:
        return False
    return combatant_distance(remover, target) <= action.range_ft


def tracked_spell_effects(
    remover: EncounterCombatant,
    setup: EncounterSetup,
    action: EffectRemovalAction,
) -> list[TrackedSpellEffect]:
    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    found: dict[tuple[str, str, str], TrackedSpellEffect] = {}
    for target in members:
        if not _target_allowed(remover, target, action):
            continue
        for modifier in target.state.active_modifiers:
            source = by_id.get(modifier.source_id)
            if source is None:
                continue
            level = _spell_level(source, modifier.source_effect_id)
            if level is None:
                continue
            key = (target.combatant_id, source.combatant_id, modifier.source_effect_id)
            found[key] = TrackedSpellEffect(target, source, modifier.source_effect_id, level)
    return sorted(
        found.values(),
        key=lambda item: (-item.spell_level, combatant_distance(remover, item.target), item.effect_id),
    )


def choose_effect_removal_action(
    remover: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[EffectRemovalAction, TrackedSpellEffect] | None:
    for action in remover.state.template.effect_removal_actions:
        if not is_available(remover.state, action.action_cost):
            continue
        if action.expends_spell_slot and not slot_spell_available(remover.state, turn_key):
            continue
        if action.resource_id is not None:
            resource = next((item for item in remover.state.resources if item.id == action.resource_id), None)
            if resource is None or resource.current_uses < action.resource_cost:
                continue
        effects = tracked_spell_effects(remover, setup, action)
        if effects:
            return action, effects[0]
    return None


def resolve_effect_removal(
    sequence: int,
    round_number: int,
    remover: EncounterCombatant,
    setup: EncounterSetup,
    action: EffectRemovalAction,
    effect: TrackedSpellEffect,
    dice: DiceProvider,
    turn_key: str,
) -> BattleEvent:
    try:
        if effect not in tracked_spell_effects(remover, setup, action):
            raise ValueError("Tracked spell effect is no longer a legal removal target.")
        spend(remover.state, action.action_cost)
        remaining = None
        if action.resource_id is not None:
            resource = next(item for item in remover.state.resources if item.id == action.resource_id)
            if action.expends_spell_slot:
                mark_slot_spell_cast(remover.state, turn_key)
            resource.current_uses -= action.resource_cost
            remaining = resource.current_uses
        check = None
        succeeded = True
        dc = None
        if effect.spell_level > action.auto_remove_max_level:
            scores = remover.state.template.ability_scores
            if scores is None:
                raise ValueError("Effect-removal ability check requires certified ability scores.")
            dc = 10 + effect.spell_level
            check = roll_d20(dice, scores.modifier(action.casting_ability), RollMode.NORMAL)
            succeeded = check.total >= dc
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
        raise
    except Exception as exc:
        logger.exception("Effect removal failed for %s.", remover.combatant_id)
        raise RuntimeError("Tracked spell effect removal could not be resolved.") from exc
