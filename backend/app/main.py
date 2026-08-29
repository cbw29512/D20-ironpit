from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.combat.dice import SecureDiceProvider
from app.combat.encounter_engine import run_encounter
from app.combat.encounter_setup import build_encounter_setup
from app.combat.engine import run_duel
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.roster import build_arena_roster
from app.domain.models import (
    ArenaRoster,
    BattleResult,
    DemoRoster,
    EncounterBattleResult,
    EncounterSelection,
    EncounterSetup,
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Iron Pit API", version="0.1.0")
origins = [
    item.strip()
    for item in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080",
    ).split(",")
    if item.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Health endpoint failed.")
        raise HTTPException(status_code=500, detail="Health check failed.") from exc


@app.get("/api/roster", response_model=ArenaRoster)
def get_arena_roster() -> ArenaRoster:
    try:
        return build_arena_roster()
    except Exception as exc:
        logger.exception("Arena roster API failed.")
        raise HTTPException(status_code=500, detail="Arena roster could not be loaded.") from exc


@app.post("/api/encounters/setup", response_model=EncounterSetup)
def create_encounter_setup(selection: EncounterSelection) -> EncounterSetup:
    try:
        return build_encounter_setup(selection)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Encounter setup API failed.")
        raise HTTPException(status_code=500, detail="Encounter setup could not be created.") from exc


@app.post("/api/encounters/fight", response_model=EncounterBattleResult)
def create_encounter_battle(selection: EncounterSelection) -> EncounterBattleResult:
    try:
        return run_encounter(selection, SecureDiceProvider())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Encounter fight API failed.")
        raise HTTPException(status_code=500, detail="Encounter fight could not be completed.") from exc


@app.get("/api/roster/demo", response_model=DemoRoster)
def get_demo_roster() -> DemoRoster:
    try:
        return DemoRoster(
            fighter=build_demo_fighter(),
            monster=build_goblin_warrior(),
        )
    except Exception as exc:
        logger.exception("Demo roster API failed.")
        raise HTTPException(status_code=500, detail="Demo roster could not be loaded.") from exc


@app.post("/api/battles/demo", response_model=BattleResult)
def create_demo_battle() -> BattleResult:
    try:
        return run_duel(
            build_demo_fighter(),
            build_goblin_warrior(),
            SecureDiceProvider(),
            starting_distance_ft=5,
        )
    except Exception as exc:
        logger.exception("Demo battle API failed.")
        raise HTTPException(status_code=500, detail="Battle could not be completed.") from exc


@app.post("/api/battles/demo-ranged", response_model=BattleResult)
def create_ranged_demo_battle() -> BattleResult:
    try:
        return run_duel(
            build_demo_fighter(),
            build_goblin_warrior(),
            SecureDiceProvider(),
            starting_distance_ft=90,
        )
    except Exception as exc:
        logger.exception("Ranged demo battle API failed.")
        raise HTTPException(status_code=500, detail="Ranged battle could not be completed.") from exc
