from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.combat.dice import SecureDiceProvider
from app.combat.engine import run_duel
from app.content.scenarios import build_rogue_ambush_setup
from app.content.test_roster import (
    build_test_catalog,
    build_test_character,
    build_test_monster,
    get_monster_opening_mode,
    get_monster_starting_distance,
)
from app.domain.models import BattleResult, CombatantTemplate, DuelMode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/test", tags=["test-arena"])


@router.get("/roster", response_model=dict[str, list[CombatantTemplate]])
def get_test_roster() -> dict[str, list[CombatantTemplate]]:
    try:
        return build_test_catalog()
    except Exception as exc:
        logger.exception("Test roster API failed.")
        raise HTTPException(status_code=500, detail="Test roster could not be loaded.") from exc


def _run_selected(
    character_id: str,
    monster_id: str,
    mode: DuelMode,
    starting_distance_ft: int | None = None,
) -> BattleResult:
    character = build_test_character(character_id)
    monster = build_test_monster(monster_id)
    distance = starting_distance_ft if starting_distance_ft is not None else (
        5 if mode is DuelMode.MELEE else 20
    )
    return run_duel(
        character,
        monster,
        SecureDiceProvider(),
        starting_distance_ft=distance,
        duel_mode=mode,
    )


@router.post("/fight/{character_id}/{monster_id}", response_model=BattleResult)
def create_test_fight(character_id: str, monster_id: str) -> BattleResult:
    try:
        return _run_selected(
            character_id,
            monster_id,
            get_monster_opening_mode(monster_id),
            get_monster_starting_distance(monster_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Automatic test fight API failed.")
        raise HTTPException(status_code=500, detail="Test fight could not be completed.") from exc


@router.post("/battle/{character_id}/{monster_id}/{mode}", response_model=BattleResult)
def create_test_battle(character_id: str, monster_id: str, mode: DuelMode) -> BattleResult:
    try:
        if mode is DuelMode.OPEN:
            raise ValueError("Test arena requires a controlled mode.")
        return _run_selected(character_id, monster_id, mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Selectable test battle API failed.")
        raise HTTPException(status_code=500, detail="Test battle could not be completed.") from exc


@router.post("/ambush/{monster_id}", response_model=BattleResult)
def create_mara_ambush(monster_id: str) -> BattleResult:
    try:
        rogue = build_test_character("mara-vale-l1")
        monster = build_test_monster(monster_id)
        visibility, encounter_setup = build_rogue_ambush_setup(rogue, monster)
        return run_duel(
            rogue,
            monster,
            SecureDiceProvider(),
            starting_distance_ft=60,
            visibility_by_actor=visibility,
            encounter_setup=encounter_setup,
            duel_mode=DuelMode.RANGED,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Selectable Rogue ambush API failed.")
        raise HTTPException(status_code=500, detail="Rogue ambush could not be completed.") from exc
