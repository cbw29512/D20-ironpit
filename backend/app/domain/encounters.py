from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.combatants import CombatantState


class EncounterParticipantRequest(BaseModel):
    instance_id: str = Field(min_length=1)
    combatant_id: str = Field(min_length=1)
    side_id: str = Field(min_length=1)
    starting_position_ft: int = Field(default=0, ge=0, le=5000)


class EncounterRequest(BaseModel):
    participants: list[EncounterParticipantRequest] = Field(min_length=2, max_length=20)


class EncounterParticipantState(BaseModel):
    side_id: str = Field(min_length=1)
    position_ft: int = Field(ge=0, le=5000)
    combatant: CombatantState


class EncounterState(BaseModel):
    participants: list[EncounterParticipantState] = Field(min_length=2, max_length=20)

    def living_on_side(self, side_id: str) -> list[EncounterParticipantState]:
        return [
            item
            for item in self.participants
            if item.side_id == side_id and item.combatant.is_alive
        ]

    def enemies_of(self, participant: EncounterParticipantState) -> list[EncounterParticipantState]:
        return [
            item
            for item in self.participants
            if item.side_id != participant.side_id and item.combatant.is_alive
        ]


def distance_between(
    first: EncounterParticipantState,
    second: EncounterParticipantState,
) -> int:
    return abs(first.position_ft - second.position_ft)
