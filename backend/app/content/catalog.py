from __future__ import annotations

import logging
from collections.abc import Callable

from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_monsters import build_ogre, build_skeleton
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
            RulesCoverageItem(feature_id="advantage-extra-damage", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="nimble-escape",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Current arena policy does not yet use Disengage or Hide.",
            ),
        ],
    )


def _skeleton_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_skeleton(),
        tags=["monster", "skeleton", "undead", "melee", "ranged", "cr-1-4"],
        rules_coverage=[
            RulesCoverageItem(feature_id="shortsword", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="shortbow", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="bludgeoning-vulnerability", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="poison-damage-immunity", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="condition-immunities",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Exhaustion and Poisoned are not yet modeled as arena conditions.",
            ),
        ],
    )


def _ogre_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_ogre(),
        tags=["monster", "ogre", "giant", "melee", "thrown", "cr-2"],
        rules_coverage=[
            RulesCoverageItem(feature_id="greatclub", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="javelin", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="thrown-weapon-range", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="javelin-inventory",
                coverage=RulesCoverage.ARENA_ASSUMPTION,
                note="The SRD stat block lists three Javelins; inventory depletion is not yet tracked.",
            ),
        ],
    )


_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "aldric-vane-l1": _fighter_entry,
    "srd-goblin-warrior": _goblin_entry,
    "srd-skeleton": _skeleton_entry,
    "srd-ogre": _ogre_entry,
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


def _list_catalog(kind: str) -> list[CatalogEntry]:
    try:
        return [entry for builder in _BUILDERS.values() if (entry := builder()).combatant.kind == kind]
    except Exception as exc:
        logger.exception("%s catalog build failed.", kind.title())
        raise RuntimeError(f"{kind.title()} catalog could not be built.") from exc


def list_character_catalog() -> list[CatalogEntry]:
    return _list_catalog("character")


def list_monster_catalog() -> list[CatalogEntry]:
    return _list_catalog("monster")
