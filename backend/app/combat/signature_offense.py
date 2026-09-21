from __future__ import annotations

import logging

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.pit_policy import save_distance, target_order
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _single_choice(actor: EncounterCombatant, setup: EncounterSetup):
    for target in target_order(actor, setup):
        for action in actor.state.template.saving_throw_actions:
            if action.resource_id is None or action.area is not None:
                continue
            distance = save_distance(actor, target, action.range_ft)
            if legal_save_action(action, target, distance):
                return target, action, distance
    return None


def resolve_signature_offense(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int] | None:
    """Use a legal resource-backed save power before ordinary attacks."""
    try:
        area = choose_area_save(actor, setup, resource_only=True)
        if area is not None:
            action, placement = area
            return resolve_area_save(
                sequence, round_number, actor, setup, action, placement, dice,
            )
        chosen = _single_choice(actor, setup)
        if chosen is None:
            return None
        target, action, distance = chosen
        states = [member.state for member in [*setup.heroes, *setup.monsters]]
        return resolve_save_event_chain(
            sequence, round_number, actor, target, action, distance, dice, setup,
            turn_key=turn_key, affected_states=states,
        )
    except Exception as exc:
        logger.exception("Failed signature offense selection for %s.", actor.combatant_id)
        raise RuntimeError("Signature offense could not be resolved.") from exc
