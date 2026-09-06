from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from app.content.arena_eligibility import deferred_environment_reason
from app.content.blocker_yield import build_blocker_signatures, single_family_yields
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.roster_mechanic_requirements import derive_roster_mechanic_requirements
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _NONCOMBAT, _source_blockers


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data" / "combat_engine_coverage_v1.json"


def _capability_statuses() -> dict[str, str]:
    payload = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    return {str(item["id"]): str(item["status"]) for item in payload["capabilities"]}


def _monster_backlog() -> tuple[
    dict[str, list[str]],
    list[str],
    list[str],
    int,
]:
    rows = load_monster_rows()
    monster_names = {str(row["name"]) for row in rows}
    ready_names = {
        card.name
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    blockers_by_name: dict[str, list[str]] = {}
    environment_deferred: list[str] = []
    noncombat_deferred: list[str] = []

    for row in rows:
        name = str(row["name"])
        if name in ready_names:
            continue
        if deferred_environment_reason(row["speed"]) is not None:
            environment_deferred.append(name)
            continue
        blockers = _source_blockers(row, monster_names)
        if blockers == [_NONCOMBAT]:
            noncombat_deferred.append(name)
            continue
        blockers_by_name[name] = blockers or ["unclassified-source-audit-gap"]

    return blockers_by_name, environment_deferred, noncombat_deferred, len(ready_names)


def _monster_family_rows(blockers_by_name: dict[str, list[str]]) -> list[tuple[str, int, int]]:
    affected: dict[str, set[str]] = defaultdict(set)
    for monster, blockers in blockers_by_name.items():
        for blocker in blockers:
            affected[blocker].add(monster)

    signatures = build_blocker_signatures(blockers_by_name)
    immediate = single_family_yields(signatures)
    return sorted(
        (
            family,
            len(immediate.get(family, ())),
            len(monsters),
        )
        for family, monsters in affected.items()
    , key=lambda row: (-row[1], -row[2], row[0]))


def _hero_rows(statuses: dict[str, str]) -> list[tuple[str, str, int, int, str]]:
    rows: list[tuple[str, str, int, int, str]] = []
    for requirement in derive_roster_mechanic_requirements(statuses):
        if requirement.status in {"supported", "arena_out_of_scope"}:
            continue
        classes = {owner.split("/", 1)[0] for owner in requirement.owners}
        rows.append((
            requirement.id,
            requirement.status,
            requirement.demand_count,
            len(classes),
            ",".join(requirement.kinds),
        ))
    return sorted(rows, key=lambda row: (-row[2], -row[3], row[0]))


def main() -> None:
    statuses = _capability_statuses()
    blockers_by_name, environment_deferred, noncombat_deferred, ready_count = _monster_backlog()
    monster_rows = _monster_family_rows(blockers_by_name)
    hero_rows = _hero_rows(statuses)

    print(
        "UNIVERSAL_ENGINE_BASELINE"
        f"\tmonster_ready={ready_count}"
        f"\tmonster_actionable_blocked={len(blockers_by_name)}"
        f"\tmonster_deferred={len(environment_deferred) + len(noncombat_deferred)}"
        f"\tmonster_families={len(monster_rows)}"
        f"\tplanned_hero_mechanics={len(hero_rows)}"
    )

    print("UNIVERSAL_ENGINE_MONSTER_FAMILIES")
    for family, immediate_unlocks, affected in monster_rows:
        print(
            "UNIVERSAL_MONSTER_FAMILY"
            f"\t{family}"
            f"\timmediate_unlocks={immediate_unlocks}"
            f"\taffected={affected}"
            f"\tengine_status={statuses.get(family, 'unmapped')}"
        )

    print("UNIVERSAL_ENGINE_HERO_MECHANICS")
    for mechanic_id, status, owner_count, class_count, kinds in hero_rows:
        print(
            "UNIVERSAL_HERO_MECHANIC"
            f"\t{mechanic_id}"
            f"\towners={owner_count}"
            f"\tclasses={class_count}"
            f"\tstatus={status}"
            f"\tkinds={kinds}"
        )

    monster_family_ids = {row[0] for row in monster_rows}
    hero_mechanic_ids = {row[0] for row in hero_rows}
    for shared_id in sorted(monster_family_ids & hero_mechanic_ids):
        print(f"UNIVERSAL_EXACT_CROSS_ROSTER_MATCH\t{shared_id}")


if __name__ == "__main__":
    main()
