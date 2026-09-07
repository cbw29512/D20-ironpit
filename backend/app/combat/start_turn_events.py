from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.recharge import resolve_recharge_start_of_turn
from app.combat.zero_hp import _mark_dead, restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_start_turn_progression_healing(
    sequence: int, round_number: int, member: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    features = member.state.template.progression_features
    bonus = features.bloodied_start_turn_healing_bonus
    abilities = member.state.template.ability_scores
    if bonus <= 0 or abilities is None or member.state.is_dead or member.state.current_hp <= 0:
        return [], sequence
    if member.state.current_hp > effective_max_hp(member.state) // 2:
        return [], sequence
    amount = bonus + abilities.modifier("constitution")
    hp_before = member.state.current_hp
    healed = restore_hit_points(member.state, amount)
    if healed <= 0:
        return [], sequence
    return [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=member.combatant_id, target_name=member.state.template.name,
        feature_id="bloodied-start-turn-healing", hp_before=hp_before, hp_after=member.state.current_hp,
        animation="healing", description=f"{member.state.template.name} regains {healed} HP at the start of the turn.",
    )], sequence + 1


def resolve_start_turn_regeneration(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    """Resolve a declarative Regeneration trait before the creature acts."""
    profile = member.state.template.regeneration
    if profile is None or member.state.is_dead:
        return [], sequence
    suppressed = member.state.regeneration_suppressed_next_turn
    member.state.regeneration_suppressed_next_turn = False
    if suppressed:
        if member.state.current_hp == 0 and profile.delays_death_at_zero:
            _mark_dead(member.state)
            return [BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=member.combatant_id, actor_name=member.state.template.name,
                feature_id="regeneration", is_dead=True, animation="death",
                description=f"{member.state.template.name}'s Regeneration is suppressed and it dies at 0 HP.",
            )], sequence + 1
        return [BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=member.combatant_id, actor_name=member.state.template.name,
            feature_id="regeneration", animation="condition",
            description=f"{member.state.template.name}'s Regeneration is suppressed this turn.",
        )], sequence + 1
    hp_before = member.state.current_hp
    healed = restore_hit_points(member.state, profile.amount)
    if healed <= 0:
        return [], sequence
    return [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        feature_id="regeneration", hp_before=hp_before, hp_after=member.state.current_hp,
        animation="healing", description=f"{member.state.template.name} regenerates {healed} HP.",
    )], sequence + 1


def resolve_start_turn_recharges(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve every spent declarative Recharge resource at START_OF_TURN."""
    try:
        events: list[BattleEvent] = []
        for definition in member.state.template.resources:
            if definition.recharge is None:
                continue
            result = resolve_recharge_start_of_turn(member.state, definition.id, definition.recharge, dice)
            if result.roll is None:
                continue
            outcome = "recharges" if result.recharged else "does not recharge"
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=member.combatant_id, actor_name=member.state.template.name,
                feature_id=definition.id, resource_remaining=result.resource_remaining,
                animation="recharge",
                description=f"{member.state.template.name} rolls {result.roll} for {definition.name} Recharge and {outcome}.",
            ))
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Start-turn Recharge failed for %s.", member.combatant_id)
        raise RuntimeError("Start-turn Recharge could not be resolved.") from exc
