"""Generic movement-through-destroyed-section save, with source-owned wall lifetime."""
from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge

logger = logging.getLogger(__name__)


def resolve_destroyed_barrier_crossing(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    before: GridPosition,
    after: GridPosition,
    turn_key: str,
):
    """Resolve each completed crossing of an active destroyed-section air sheet.

    Intact walls block movement upstream. This only handles a *finished* legal
    step across a destroyed section; it never guesses damage based on proximity.
    """
    try:
        if abs(before.x - after.x) + abs(before.y - after.y) != 1:
            raise ValueError("Barrier air crossing requires one legal grid step.")
        crossed = GridBarrierEdge(first=before, second=after).canonical_key()
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        events = []
        for wall in list(setup.persistent_barriers):
            if round_number >= wall.expires_round:
                continue
            if not any(not section.destroyed and section.current_hp > 0
                       for section in wall.sections):
                continue  # No frigid air after the rest of the wall vanishes.
            owner = members.get(wall.source_id)
            if owner is None:
                raise ValueError("Persistent barrier source is no longer in the fight.")
            if (wall.ends_on_source_death and owner.state.is_dead
                    or wall.ends_on_source_incapacitated and is_incapacitated(owner.state)):
                continue
            for section in wall.sections:
                save = section.destroyed_section_crossing_save
                if not section.destroyed or save is None:
                    continue
                if not any(edge.canonical_key() == crossed for edge in section.edges):
                    continue
                # Range 0 is correct: the wall is the local save origin, not
                # the owner's position. No new Action or Recharge is spent.
                more, sequence = resolve_save_event_chain(
                    sequence, round_number, owner, mover, save, 0, dice, setup,
                    turn_key=turn_key, spend_action=False, check_resource=False,
                    spend_resource=False,
                    affected_states=[member.state for member in members.values()],
                )
                events.extend(more)
        return events, sequence
    except ValueError:
        raise
    except Exception:
        logger.exception("Destroyed barrier crossing save failed for %s", mover.combatant_id)
        raise
