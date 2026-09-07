from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.encounters import EncounterSelection

TurboOutcome = Literal["heroes_win", "monsters_win", "draw"]
MAX_TURBO_FIGHTS = 10_000
MAX_REPLAY_SEED = (2**63) - 1


class EncounterReplayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selection: EncounterSelection
    seed: int = Field(ge=0, le=MAX_REPLAY_SEED)


class TurboBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selection: EncounterSelection
    fights: int = Field(ge=1, le=MAX_TURBO_FIGHTS)
    batch_seed: int | None = Field(default=None, ge=0, le=MAX_REPLAY_SEED)


class TurboFightSummary(BaseModel):
    fight_number: int = Field(ge=1)
    seed: int = Field(ge=0, le=MAX_REPLAY_SEED)
    outcome: TurboOutcome
    rounds: int = Field(ge=0)
    hero_survivors: int = Field(ge=0, le=6)
    monster_survivors: int = Field(ge=0, le=6)
    safety_stop: bool = False


class TurboFightError(BaseModel):
    fight_number: int = Field(ge=1)
    seed: int = Field(ge=0, le=MAX_REPLAY_SEED)
    error_type: str
    message: str


class TurboBatchResult(BaseModel):
    batch_seed: int = Field(ge=0, le=MAX_REPLAY_SEED)
    requested_fights: int = Field(ge=1)
    valid_fights: int = Field(ge=0)
    engine_errors: int = Field(ge=0)
    heroes_wins: int = Field(ge=0)
    monsters_wins: int = Field(ge=0)
    draws: int = Field(ge=0)
    heroes_win_rate: float = Field(ge=0, le=100)
    monsters_win_rate: float = Field(ge=0, le=100)
    draw_rate: float = Field(ge=0, le=100)
    average_rounds: float = Field(ge=0)
    fastest_fight_number: int | None = Field(default=None, ge=1)
    longest_fight_number: int | None = Field(default=None, ge=1)
    fights: list[TurboFightSummary] = Field(default_factory=list)
    errors: list[TurboFightError] = Field(default_factory=list)