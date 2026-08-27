from __future__ import annotations

from collections.abc import Callable

from app.content.srd_undead import build_ghoul
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem


def _ghoul_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_ghoul(),
        tags=["monster", "ghoul", "undead", "melee", "paralyzed", "cr-1"],
        rules_coverage=[
            RulesCoverageItem(feature_id="bite", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="multiattack", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="claw", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="claw-paralysis-save",
                coverage=RulesCoverage.FULLY_IMPLEMENTED,
            ),
            RulesCoverageItem(
                feature_id="claw-action-policy",
                coverage=RulesCoverage.ARENA_ASSUMPTION,
                note="Baseline duel policy still prioritizes the listed Multiattack damage routine.",
            ),
            RulesCoverageItem(
                feature_id="charmed-exhaustion-immunity",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Immunity data is stored; Charmed and Exhaustion mechanics are not active yet.",
            ),
        ],
    )


UNDEAD_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "srd-ghoul": _ghoul_entry,
}
