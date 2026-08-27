from __future__ import annotations

from collections.abc import Callable

from app.content.demo import build_demo_fighter
from app.content.gladiators import build_darius_flint, build_mara_stone, build_vera_ash
from app.domain.catalog import CatalogEntry, RulesCoverage, RulesCoverageItem
from app.domain.models import CombatantTemplate


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
            RulesCoverageItem(feature_id="weapon-mastery", coverage=RulesCoverage.UNSUPPORTED),
        ],
    )


def _advanced_fighter_entry(
    builder: Callable[[], CombatantTemplate],
    level: int,
) -> CatalogEntry:
    combatant = builder()
    return CatalogEntry(
        combatant=combatant,
        tags=["character", "fighter", "melee", "shield", "second-wind", f"level-{level}"],
        rules_coverage=[
            RulesCoverageItem(
                feature_id="extra-attack",
                coverage=RulesCoverage.FULLY_IMPLEMENTED,
                note=f"Attack action resolves {combatant.attacks_per_action} attacks.",
            ),
            RulesCoverageItem(feature_id="second-wind", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(feature_id="action-surge", coverage=RulesCoverage.FULLY_IMPLEMENTED),
            RulesCoverageItem(
                feature_id="action-surge-policy",
                coverage=RulesCoverage.ARENA_ASSUMPTION,
                note="Arena spends Action Surge after the normal action while the opponent survives.",
            ),
            RulesCoverageItem(
                feature_id="defense-fighting-style",
                coverage=RulesCoverage.FULLY_IMPLEMENTED,
                note="Defense is baked into this fixed pregen's AC 19.",
            ),
            RulesCoverageItem(feature_id="fighter-subclass", coverage=RulesCoverage.UNSUPPORTED),
            RulesCoverageItem(feature_id="weapon-mastery", coverage=RulesCoverage.UNSUPPORTED),
            RulesCoverageItem(
                feature_id="other-level-features",
                coverage=RulesCoverage.UNSUPPORTED,
                note="Other Fighter features gained by this level are not yet resolved by the arena.",
            ),
        ],
    )


CHARACTER_BUILDERS: dict[str, Callable[[], CatalogEntry]] = {
    "aldric-vane-l1": _aldric_entry,
    "mara-stone-l5": lambda: _advanced_fighter_entry(build_mara_stone, 5),
    "darius-flint-l11": lambda: _advanced_fighter_entry(build_darius_flint, 11),
    "vera-ash-l20": lambda: _advanced_fighter_entry(build_vera_ash, 20),
}
