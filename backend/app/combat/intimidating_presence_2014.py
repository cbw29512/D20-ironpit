from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)
FEATURE_ID = "intimidating-presence-2014"
FRIGHTENED = "frightened"


def _immunity_key(source_id: str) -> str:
    return f"{FEATURE_ID}:immune:{source_id}"


def _active_effect(target: EncounterCombatant, source_id: str):
    return next((effect for effect in target.state.timed_effects
                 if effect.effect_id == FRIGHTENED and effect.source_id == source_id
                 and effect.source_effect_id == FEATURE_ID), None)


def _can_perceive_source(target: EncounterCombatant) -> bool:
    return not (has_condition(target.state, "blinded") and has_condition(target.state, "deafened"))


def can_use_presence(actor: EncounterCombatant, target: EncounterCombatant) -> bool:
    dc = actor.state.template.progression_features.intimidating_presence_2014_dc
    return bool(
        actor.state.template.ruleset == "2014" and dc > 0 and is_available(actor.state, "action")
        and target.state.is_alive and not target.state.is_dead and combatant_distance(actor, target) <= 30
        and _can_perceive_source(target) and not condition_is_immune(target.state, FRIGHTENED)
        and _immunity_key(actor.combatant_id) not in target.state.feature_last_turn_keys
        and _active_effect(target, actor.combatant_id) is None
    )


def resolve_intimidating_presence(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant, dice,
) -> BattleEvent | None:
    """Resolve the 2014 Berserker action without approximating a failed or successful save."""
    try:
        if not can_use_presence(actor, target):
            return None
        dc = actor.state.template.progression_features.intimidating_presence_2014_dc
        roll, succeeded = resolve_saving_throw(target.state, "wisdom", dc, dice)
        spend(actor.state, "action")
        applied: list[str] = []
        if succeeded:
            target.state.feature_last_turn_keys[_immunity_key(actor.combatant_id)] = "24h"
        else:
            effect = apply_timed_condition(
                target.state, FRIGHTENED, actor.combatant_id, source_effect_id=FEATURE_ID,
                applied_round=round_number, expires_round=round_number + 1,
                expiry_timing="source_turn_end", use_default_poison_recovery=False,
            )
            if effect:
                applied.append(effect)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=actor.combatant_id, actor_name=actor.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability="wisdom", save_dc=dc, save_succeeded=succeeded,
            applied_condition_ids=applied, feature_id=FEATURE_ID, animation="fear",
            description=(f"{actor.state.template.name} uses Intimidating Presence; "
                         f"{target.state.template.name} {'resists' if succeeded else 'is Frightened'}."),
        )
    except Exception:
        logger.exception("2014 Intimidating Presence failed for %s.", actor.combatant_id)
        raise


def extend_intimidating_presence(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
) -> BattleEvent | None:
    """Spend the optional later Action to extend the same failed-save effect by one source turn."""
    effect = _active_effect(target, actor.combatant_id)
    if effect is None or not is_available(actor.state, "action") or combatant_distance(actor, target) > 60:
        return None
    spend(actor.state, "action")
    effect.expires_round = round_number + 1
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=actor.combatant_id, actor_name=actor.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        feature_id=FEATURE_ID, animation="fear",
        description=f"{actor.state.template.name} extends Intimidating Presence on {target.state.template.name}.",
    )


def end_invalid_presence(
    sequence: int, round_number: int, target: EncounterCombatant, setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """End the feature when the frightened creature ends its turn beyond 60 feet or without line of sight."""
    events: list[BattleEvent] = []
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    for effect in list(target.state.timed_effects):
        if effect.source_effect_id != FEATURE_ID:
            continue
        source = members.get(effect.source_id)
        if source is None:
            continue
        line_of_sight = not has_condition(target.state, "blinded") and not has_condition(source.state, "invisible")
        if line_of_sight and combatant_distance(target, source) <= 60:
            continue
        removed = remove_effect_group(target.state, effect)
        if not removed:
            continue
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=target.combatant_id, actor_name=target.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            removed_condition_ids=removed, feature_id=FEATURE_ID, animation="condition-ended",
            description=f"Intimidating Presence ends on {target.state.template.name}.",
        ))
        sequence += 1
    return events, sequence
