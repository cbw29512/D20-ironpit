from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.combat.dice import SecureDiceProvider
from app.combat.engine import run_duel
from app.content.catalog import (
    CatalogEntryNotFoundError,
    list_character_catalog,
    list_monster_catalog,
)
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattleRequest, BattleResult, CatalogEntry, DemoRoster
from app.services.catalog_battles import CatalogBattleValidationError, run_catalog_battle

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Iron Pit API", version="0.2.0")
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


@app.get("/api/catalog/characters", response_model=list[CatalogEntry])
def get_character_catalog() -> list[CatalogEntry]:
    try:
        return list_character_catalog()
    except Exception as exc:
        logger.exception("Character catalog API failed.")
        raise HTTPException(status_code=500, detail="Character catalog could not be loaded.") from exc


@app.get("/api/catalog/monsters", response_model=list[CatalogEntry])
def get_monster_catalog() -> list[CatalogEntry]:
    try:
        return list_monster_catalog()
    except Exception as exc:
        logger.exception("Monster catalog API failed.")
        raise HTTPException(status_code=500, detail="Monster catalog could not be loaded.") from exc


@app.post("/api/battles", response_model=BattleResult)
def create_catalog_battle(request: BattleRequest) -> BattleResult:
    try:
        return run_catalog_battle(request, SecureDiceProvider())
    except CatalogEntryNotFoundError as exc:
        logger.warning("Catalog battle lookup failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CatalogBattleValidationError as exc:
        logger.warning("Catalog battle validation failed: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Catalog battle API failed.")
        raise HTTPException(status_code=500, detail="Battle could not be completed.") from exc


@app.get("/api/roster/demo", response_model=DemoRoster)
def get_demo_roster() -> DemoRoster:
    try:
        return DemoRoster(fighter=build_demo_fighter(), monster=build_goblin_warrior())
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
