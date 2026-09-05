from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.combat.dice import SecureDiceProvider
from app.combat.encounter_engine import run_encounter
from app.combat.encounter_setup import build_encounter_setup
from app.content.audited_fighter import build_karnok_stoneward
from app.content.catalog import build_full_content_catalog
from app.content.demo import build_goblin_warrior
from app.content.readiness import assert_public_selection_runnable
from app.content.roster import build_arena_roster
from app.domain.catalog import FullContentCatalog
from app.domain.models import ArenaRoster, DemoRoster, EncounterBattleResult, EncounterSelection, EncounterSetup

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
    return {"status": "ok"}


@app.get("/api/catalog", response_model=FullContentCatalog)
def get_full_content_catalog() -> FullContentCatalog:
    try:
        return build_full_content_catalog()
    except Exception as exc:
        logger.exception("Full content catalog API failed.")
        raise HTTPException(status_code=500, detail="Content catalog could not be loaded.") from exc


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
        assert_public_selection_runnable(selection)
        return build_encounter_setup(selection)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Encounter setup API failed.")
        raise HTTPException(status_code=500, detail="Encounter setup could not be created.") from exc


@app.post("/api/encounters/fight", response_model=EncounterBattleResult)
def create_encounter_battle(selection: EncounterSelection) -> EncounterBattleResult:
    try:
        assert_public_selection_runnable(selection)
        return run_encounter(selection, SecureDiceProvider())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Encounter fight API failed.")
        raise HTTPException(status_code=500, detail="Encounter fight could not be completed.") from exc


@app.get("/api/roster/demo", response_model=DemoRoster)
def get_demo_roster() -> DemoRoster:
    try:
        return DemoRoster(fighter=build_karnok_stoneward(), monster=build_goblin_warrior())
    except Exception as exc:
        logger.exception("Demo roster API failed.")
        raise HTTPException(status_code=500, detail="Demo roster could not be loaded.") from exc
