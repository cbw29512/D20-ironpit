from __future__ import annotations

from collections.abc import Callable

from app.content.srd_beasts import build_giant_crab, build_wolf
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


BEAST_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "srd-wolf": _wolf_entry,
    "srd-giant-crab": _giant_crab_entry,
}
