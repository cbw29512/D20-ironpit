from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.engine import run_duel
from app.content.catalog import get_catalog_entry
from app.domain.catalog import BattleRequest
from app.domain.events import BattleResult

logger = logging.getLogger(__name__)


class CatalogBattleValidationError(ValueError):
    pass


def run_catalog_battle(request: BattleRequest, dice: DiceProvider) -> BattleResult:
    try:
        character = get_catalog_entry(request.character_id)
        monster = get_catalog_entry(request.monster_id)

        if character.combatant.kind != "character":
            raise CatalogBattleValidationError("character_id must identify a character.")
        if monster.combatant.kind != "monster":
            raise CatalogBattleValidationError("monster_id must identify a monster.")
        if not character.battle_ready or not monster.battle_ready:
            raise CatalogBattleValidationError("Selected combatant is not battle-ready.")

        return run_duel(
            character.combatant,
            monster.combatant,
            dice,
            starting_distance_ft=request.starting_distance_ft,
        )
    except CatalogBattleValidationError:
        logger.warning(
            "Catalog battle rejected: character=%s monster=%s.",
            request.character_id,
            request.monster_id,
        )
        raise
    except Exception:
        logger.exception(
            "Catalog battle failed: character=%s monster=%s.",
            request.character_id,
            request.monster_id,
        )
        raise
