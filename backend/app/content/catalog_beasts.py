from __future__ import annotations

from collections.abc import Callable

from app.content.srd_beasts import build_giant_crab, build_lion, build_wolf
from app.content.srd_spiders import build_giant_spider
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem


def _wolf_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_wolf(),
        tags=["monster", "wolf", "beast", "melee", "prone", "cr-1-4"],
        rules_coverage=[
            RulesCoverageItem(feature_id="bite", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="bite-prone", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="pack-tactics",
                coverage=RulesCoverage.UNSUPPORTED,
                note="The current 1v1 arena has no wolf ally that could trigger Pack Tactics.",
            ),
        ],
    )


def _giant_crab_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_giant_crab(),
        tags=["monster", "giant-crab", "beast", "melee", "grapple", "cr-1-8"],
        rules_coverage=[
            RulesCoverageItem(feature_id="claw", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="claw-grapple", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="grapple-drag-carry",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Encounter movement does not yet drag or carry a grappled target.",
            ),
            RulesCoverageItem(
                feature_id="two-claw-grapple-capacity",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Per-claw grapple occupancy matters only once multi-target combat is activated.",
            ),
            RulesCoverageItem(
                feature_id="swim-speed",
                coverage=RulesCoverage.UNSUPPORTED,
                note="The current arena is land-only.",
            ),
        ],
    )


def _lion_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_lion(),
        tags=["monster", "lion", "beast", "melee", "frightened", "cr-1"],
        rules_coverage=[
            RulesCoverageItem(feature_id="rend", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="roar", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="multiattack", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="roar-replacement-policy",
                coverage=RulesCoverage.ARENA_ASSUMPTION,
                note="Arena uses Roar when it can apply a new legal Frightened condition.",
            ),
            RulesCoverageItem(
                feature_id="pack-tactics",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Allied-position checks are deferred until multi-combatant turns activate.",
            ),
            RulesCoverageItem(
                feature_id="running-leap",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Jump and obstacle geometry are not yet modeled.",
            ),
        ],
    )


def _giant_spider_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_giant_spider(),
        tags=["monster", "giant-spider", "beast", "poison", "restrained", "cr-1"],
        rules_coverage=[
            RulesCoverageItem(feature_id="bite", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="web", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="web-recharge", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="web-object", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="spider-climb",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Wall and ceiling terrain are not yet modeled.",
            ),
            RulesCoverageItem(
                feature_id="web-walker",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Web terrain and shared-web location sensing are not yet modeled.",
            ),
        ],
    )


BEAST_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "srd-wolf": _wolf_entry,
    "srd-giant-crab": _giant_crab_entry,
    "srd-lion": _lion_entry,
    "srd-giant-spider": _giant_spider_entry,
}
