from __future__ import annotations

import logging
from collections.abc import Callable

from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem

logger = logging.getLogger(__name__)


class CatalogEntryNotFoundError(LookupError):
    pass


def _fighter_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_demo_fighter(),
        tags=["character", "fighter", "melee", "shield", "second-wind"],
        rules_coverage=[
            RulesCoverageItem(feature_id="core-melee", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="second-wind", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="fighting-style",
                coverage=RulesCoverage.ARENA_ASSUMPTION,
                note="Level 1 Fighting Style choice is not yet applied to combat math.",
            ),
            RulesCoverageItem(
                feature_id="weapon-mastery",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Weapon Mastery effects are not yet resolved by the combat engine.",
            ),
        ],
    )


def _goblin_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_goblin_warrior(),
        tags=["monster", "goblin", "melee", "ranged", "shield", "cr-1-4"],
        rules_coverage=[
            RulesCoverageItem(feature_id="scimitar", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="shortbow", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="advantage-extra-damage",
                coverage=RulesCoverage.FULLY_IMPLEMENTED,
            ),
            RulesCoverageItem(
                feature_id="nimble-escape",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Current arena policy does not yet use Disengage or Hide.",
            ),
        ],
    )


_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "aldric-vane-l1": _fighter_entry,
    "srd-goblin-warrior": _goblin_entry,
}


def get_catalog_entry(combatant_id: str) -> CatalogEntry:
    try:
        builder = _BUILDERS.get(combatant_id)
        if builder is None:
            raise CatalogEntryNotFoundError(f"Unknown combatant: {combatant_id}")
        return builder()
    except CatalogEntryNotFoundError:
        logger.warning("Catalog lookup failed for %s.", combatant_id)
        raise
    except Exception as exc:
        logger.exception("Catalog entry build failed for %s.", combatant_id)
        raise RuntimeError("Catalog entry could not be built.") from exc


def list_character_catalog() -> list[CatalogEntry]:
    try:
        return [entry for builder in _BUILDERS.values() if (entry := builder()).combatant.kind == "character"]
    except Exception as exc:
        logger.exception("Character catalog build failed.")
        raise RuntimeError("Character catalog could not be built.") from exc


def list_monster_catalog() -> list[CatalogEntry]:
    try:
        return [entry for builder in _BUILDERS.values() if (entry := builder()).combatant.kind == "monster"]
    except Exception as exc:
        logger.exception("Monster catalog build failed.")
        raise RuntimeError("Monster catalog could not be built.") from exc
