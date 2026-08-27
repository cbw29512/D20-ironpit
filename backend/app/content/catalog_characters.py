from __future__ import annotations

from collections.abc import Callable

from app.content.demo import build_demo_fighter
from app.content.gladiators import build_mara_stone
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem


def _aldric_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_demo_fighter(),
        tags=["character", "fighter", "melee", "shield", "second-wind", "level-1"],
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


def _mara_entry() -> CatalogEntry:
    return CatalogEntry(
        combatant=build_mara_stone(),
        tags=["character", "fighter", "melee", "shield", "second-wind", "level-5"],
        rules_coverage=[
            RulesCoverageItem(feature_id="extra-attack", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="second-wind", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="defense-fighting-style",
                coverage=RulesCoverage.FULLY_IMPLEMENTED,
                note="Defense is baked into this fixed pregen's AC 19.",
            ),
            RulesCoverageItem(
                feature_id="fighter-subclass",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Subclass features are not yet modeled for this development pregen.",
            ),
            RulesCoverageItem(feature_id="action-surge", coverage=RulesCoverage.UNSUPPORTED),
            RulesCoverageItem(feature_id="tactical-shift", coverage=RulesCoverage.UNSUPPORTED),
            RulesCoverageItem(feature_id="weapon-mastery", coverage=RulesCoverage.UNSUPPORTED),
        ],
    )


CHARACTER_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "aldric-vane-l1": _aldric_entry,
    "mara-stone-l5": _mara_entry,
}
