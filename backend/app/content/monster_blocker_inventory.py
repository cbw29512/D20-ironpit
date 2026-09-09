from __future__ import annotations

from collections import defaultdict

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_classifier import source_blockers
from app.domain.catalog import CoverageStatus

_NOISE_BLOCKERS = frozenset({"monster-combat-mechanics-not-compiled"})


def build_monster_blocker_inventory() -> tuple[
    dict[str, dict[str, object]], set[str], dict[str, list[str]]
]:
    rows = load_monster_rows()
    rows_by_name = {str(row["name"]): row for row in rows}
    monster_names = set(rows_by_name)
    ready_names = {
        card.name
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    blockers_by_name: dict[str, list[str]] = {}
    for row in rows:
        name = str(row["name"])
        if name in ready_names:
            continue
        blockers = source_blockers(row, monster_names)
        blockers_by_name[name] = blockers or ["unclassified-source-audit-gap"]
    return rows_by_name, ready_names, blockers_by_name


def blocker_family_incidence(blockers_by_name: dict[str, list[str]]) -> dict[str, list[str]]:
    incidence: dict[str, list[str]] = defaultdict(list)
    for name, blockers in blockers_by_name.items():
        for blocker in sorted(set(blockers) - _NOISE_BLOCKERS):
            incidence[blocker].append(name)
    return {
        blocker: sorted(names)
        for blocker, names in sorted(incidence.items(), key=lambda item: (-len(item[1]), item[0]))
    }
