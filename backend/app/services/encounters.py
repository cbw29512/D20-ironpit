from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.content.catalog import get_catalog_entry
from app.domain.encounters import EncounterParticipantState, EncounterRequest, EncounterState

logger = logging.getLogger(__name__)


class EncounterValidationError(ValueError):
    pass


def build_encounter_state(request: EncounterRequest) -> EncounterState:
    try:
        instance_ids = [item.instance_id for item in request.participants]
        if len(instance_ids) != len(set(instance_ids)):
            raise EncounterValidationError("Encounter instance_id values must be unique.")

        sides = {item.side_id for item in request.participants}
        if len(sides) < 2:
            raise EncounterValidationError("Encounter requires at least two opposing sides.")

        participants: list[EncounterParticipantState] = []
        for item in request.participants:
            entry = get_catalog_entry(item.combatant_id)
            if not entry.battle_ready:
                raise EncounterValidationError(
                    f"Combatant is not battle-ready: {item.combatant_id}"
                )
            participants.append(EncounterParticipantState(
                side_id=item.side_id,
                position_ft=item.starting_position_ft,
                combatant=build_combatant_state(entry.combatant, item.instance_id),
            ))
        return EncounterState(participants=participants)
    except EncounterValidationError:
        raise
    except Exception as exc:
        logger.exception("Encounter state construction failed.")
        raise RuntimeError("Encounter state could not be created.") from exc
