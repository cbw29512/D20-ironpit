from __future__ import annotations

from collections.abc import Callable

from app.content.demo import build_goblin_warrior
from app.content.srd_monsters import build_ogre, build_skeleton
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem


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


MONSTER_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "srd-goblin-warrior": _goblin_entry,
    "srd-skeleton": _skeleton_entry,
    "srd-ogre": _ogre_entry,
}
