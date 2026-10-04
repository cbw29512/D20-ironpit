from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.legendary_action_choice import choose_legendary_action, choose_legendary_attack
from app.combat.resources import spend_resource
from app.combat.save_targets import resolve_save_targets
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
RESOURCE_ID = "legendary-actions"


def resolve_legendary_actions_after_turn(
    sequence: int,
    round_number: int,
    just_acted: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Each other combatant may spend one legendary action option after this turn."""
    try:
        events: list[BattleEvent] = []
        others = [
            item for item in [*setup.heroes, *setup.monsters]
            if item.combatant_id != just_acted.combatant_id
        ]
        for actor in others:
            choice = choose_legendary_action(actor, setup)
            if choice is None:
                continue
            kind, selected = choice
            spend_resource(actor.state, RESOURCE_ID, selected[0].cost)
            if kind == "attack":
                option, target, attack = selected
                event = resolve_attack(
                    sequence, round_number, actor.state, target.state, attack,
                    combatant_distance(actor, target), dice,
                    actor_event_id=actor.combatant_id, target_event_id=target.combatant_id,
                    spend_action=False, off_turn=True, feature_id=option.id,
                    affected_states=[item.state for item in [*setup.heroes, *setup.monsters]],
                    reaction_setup=setup, reaction_roller=actor,
                )
                events.append(event.model_copy(update={
                    "description": (
                        f"{actor.state.template.name} uses Legendary Action: {option.name}. "
                        f"{event.description}"
                    ),
                }))
                sequence += 1
                continue
            option, action, placement = selected
            resolved, sequence = resolve_save_targets(
                sequence, round_number, actor, setup, action, placement.target_ids, dice,
                skip_range_check=True,
            )
            prefix = f"{actor.state.template.name} uses Legendary Action: {option.name}."
            for event in resolved:
                events.append(event.model_copy(update={
                    "description": f"{prefix} {event.description}",
                    "feature_id": option.id,
                }))
        return events, sequence
    except Exception:
        logger.exception("Failed legendary actions after %s.", just_acted.combatant_id)
        raise


__all__ = [
    "choose_legendary_attack",
    "choose_legendary_action",
    "resolve_legendary_actions_after_turn",
]
