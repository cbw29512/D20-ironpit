from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import can_see, has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.reactions import TurnStartSaveConditionReaction

logger = logging.getLogger(__name__)


def _eligible(
    reactor: EncounterCombatant,
    target: EncounterCombatant,
    reaction: TurnStartSaveConditionReaction,
    setup=None,
) -> bool:
    try:
        if not is_available(reactor.state, "reaction"):
            return False
        # Harmful save-condition Reactions are never chosen against a live ally.
        if reactor.side == target.side:
            return False
        if not reactor.state.is_alive or reactor.state.is_dead:
            return False
        if not target.state.is_alive or target.state.is_dead:
            return False
        if condition_is_immune(target.state, reaction.condition_id, actor=target, setup=setup):
            return False
        if has_condition(target.state, reaction.condition_id, setup=setup):
            return False
        distance = combatant_distance(reactor, target)
        if distance > reaction.range_ft:
            return False
        if reaction.requires_source_can_see_target and not can_see(reactor.state, target.state, distance):
            return False
        if reaction.requires_target_can_see_source and not can_see(target.state, reactor.state, distance):
            return False
        return True
    except Exception:
        logger.exception("Eligibility check failed for turn-start reaction on %s.", target.combatant_id)
        raise


def resolve_turn_start_save_condition_reactions(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve eligible other-creature turn-start Reactions against the creature whose turn is starting."""
    events: list[BattleEvent] = []
    try:
        reactors = [
            member for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id != target.combatant_id
        ]
        for reactor in reactors:
            reaction = reactor.state.template.turn_start_save_condition_reaction
            if reaction is None or not _eligible(reactor, target, reaction, setup):
                continue
            spend(reactor.state, "reaction")
            roll, succeeded = resolve_saving_throw(
                target.state, reaction.save_ability, reaction.save_dc, dice,
            )
            applied: list[str] = []
            if not succeeded:
                apply_timed_condition(
                    target.state,
                    reaction.condition_id,
                    reactor.combatant_id,
                    source_effect_id=reaction.source_id,
                    source_template=reactor.state.template,
                    target_actor=target, setup=setup,
                    expires_at_start_of_source_turn=False,
                    expiry_timing=reaction.expiry_timing,
                    applied_round=round_number,
                )
                applied.append(reaction.condition_id)
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=reactor.combatant_id,
                actor_name=reactor.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                feature_id=reaction.source_id,
                save_ability=reaction.save_ability,
                save_dc=reaction.save_dc,
                saving_throw_roll=roll,
                save_succeeded=succeeded,
                applied_condition_ids=applied,
                animation="fear",
                description=(
                    f"{reactor.state.template.name} uses {reaction.source_name}: "
                    f"{target.state.template.name} {'succeeds' if succeeded else 'fails'} "
                    f"the DC {reaction.save_dc} {reaction.save_ability.title()} save"
                    f"{'' if succeeded else ' and gains ' + reaction.condition_id.replace('_', ' ').title() + ' until the end of its turn'}."
                ),
            ))
            sequence += 1
            # One reaction spend per reactor; continue so multiple reactors can act
        return events, sequence
    except Exception:
        logger.exception("Turn-start save-condition Reaction failed for %s.", target.combatant_id)
        raise
