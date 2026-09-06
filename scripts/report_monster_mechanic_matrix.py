from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_mechanic_fingerprint import (
    mechanic_complexity,
    mechanic_fingerprint,
    normalized_monster_mechanics,
    source_ability_records,
)
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _NONCOMBAT, _source_blockers

_EDGE_CASES = {"summoning", "transformation", "legendary"}
_QUEUE_LIMIT = 60
_FAMILY_LIMIT = 25


def _records() -> list[dict[str, object]]:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    cards = {card.name: card for card in build_monster_catalog()}
    records: list[dict[str, object]] = []
    for row in rows:
        name = str(row["name"])
        ready = cards[name].coverage_status is CoverageStatus.RAW_READY
        mechanics = normalized_monster_mechanics(row)
        blockers = [] if ready else _source_blockers(row, names)
        ignored_noncombat = blockers == [_NONCOMBAT]
        if ignored_noncombat:
            blockers = []
        records.append({
            "monster": name,
            "ready": ready,
            "ignored_noncombat": ignored_noncombat,
            "edge_case": bool(set(mechanics) & _EDGE_CASES),
            "unsupported_families": tuple(sorted(set(blockers))),
            "unsupported_count": len(set(blockers)),
            "complexity": mechanic_complexity(mechanics),
            "mechanics": mechanics,
            "fingerprint": mechanic_fingerprint(row),
        })
    return records


def _ability_records() -> list[dict[str, object]]:
    rows = load_monster_rows()
    cards = {card.name: card for card in build_monster_catalog()}
    abilities: list[dict[str, object]] = []
    for row in rows:
        monster = str(row["name"])
        ready = cards[monster].coverage_status is CoverageStatus.RAW_READY
        for source_record in source_ability_records(row):
            record = dict(source_record)
            record["ready"] = ready
            record["complexity"] = mechanic_complexity(tuple(record["mechanics"]))
            abilities.append(record)

    families: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in abilities:
        families[str(record["equivalence_fingerprint"])].append(record)
    for members in families.values():
        ready_monsters = sorted({str(item["monster"]) for item in members if item["ready"]})
        blocked_monsters = sorted({str(item["monster"]) for item in members if not item["ready"]})
        for item in members:
            item["observed_on_raw_ready_equivalent"] = bool(ready_monsters)
            item["equivalent_ready_monsters"] = tuple(ready_monsters)
            item["equivalent_blocked_monsters"] = tuple(blocked_monsters)
            item["equivalent_blocked_count"] = len(blocked_monsters)
    return abilities


def _capability_records(abilities: list[dict[str, object]]) -> list[dict[str, object]]:
    families: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in abilities:
        families[str(record["equivalence_fingerprint"])].append(record)
    result: list[dict[str, object]] = []
    for fingerprint, members in families.items():
        ready_monsters = sorted({str(item["monster"]) for item in members if item["ready"]})
        blocked_monsters = sorted({str(item["monster"]) for item in members if not item["ready"]})
        source_names = sorted({str(item["source_name"]) for item in members})
        sections = sorted({str(item["section"]) for item in members})
        exact_fingerprints = sorted({str(item["fingerprint"]) for item in members})
        mechanics = sorted({str(mechanic) for item in members for mechanic in item["mechanics"]})
        result.append({
            "capability_id": fingerprint,
            "observed_on_raw_ready": bool(ready_monsters),
            "parse_error": any(bool(item["parse_error"]) for item in members),
            "complexity": min(int(item["complexity"]) for item in members),
            "source_ability_count": len(members),
            "monster_count": len({str(item["monster"]) for item in members}),
            "ready_monster_count": len(ready_monsters),
            "blocked_monster_count": len(blocked_monsters),
            "ready_monsters": tuple(ready_monsters),
            "blocked_monsters": tuple(blocked_monsters),
            "sections": tuple(sections),
            "source_names": tuple(source_names),
            "mechanics": tuple(mechanics),
            "exact_fingerprints": tuple(exact_fingerprints),
        })
    return result


def _queue_key(record: dict[str, object]) -> tuple[object, ...]:
    return (
        bool(record["edge_case"]),
        int(record["unsupported_count"]),
        int(record["complexity"]),
        str(record["fingerprint"]),
        str(record["monster"]),
    )


def _matrix_key(record: dict[str, object]) -> tuple[object, ...]:
    return (
        bool(record["edge_case"]),
        int(record["complexity"]),
        str(record["fingerprint"]),
        str(record["monster"]),
    )


def _write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    actionable = [record for record in records if not record["ready"] and not record["ignored_noncombat"]]
    rank_by_name = {
        str(record["monster"]): rank
        for rank, record in enumerate(sorted(actionable, key=_queue_key), start=1)
    }
    fields = (
        "work_rank", "monster", "ready", "ignored_noncombat", "edge_case",
        "unsupported_count", "complexity", "unsupported_families", "mechanics", "fingerprint",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in sorted(records, key=_matrix_key):
            row = dict(record)
            row["work_rank"] = rank_by_name.get(str(record["monster"]), "")
            row["unsupported_families"] = " | ".join(record["unsupported_families"])
            row["mechanics"] = " | ".join(record["mechanics"])
            writer.writerow({field: row[field] for field in fields})


def _write_ability_csv(path: Path, abilities: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "monster", "ready", "section", "source_name", "normalized_name", "complexity",
        "mechanics", "fingerprint", "equivalence_fingerprint", "observed_on_raw_ready_equivalent",
        "equivalent_blocked_count", "equivalent_ready_monsters", "equivalent_blocked_monsters", "parse_error",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in sorted(
            abilities,
            key=lambda item: (
                not bool(item["observed_on_raw_ready_equivalent"]),
                -int(item["equivalent_blocked_count"]),
                int(item["complexity"]),
                str(item["equivalence_fingerprint"]),
                str(item["monster"]),
                str(item["source_name"]),
            ),
        ):
            row = dict(record)
            row["mechanics"] = " | ".join(record["mechanics"])
            row["equivalent_ready_monsters"] = " | ".join(record["equivalent_ready_monsters"])
            row["equivalent_blocked_monsters"] = " | ".join(record["equivalent_blocked_monsters"])
            writer.writerow({field: row[field] for field in fields})


def _write_capability_csv(path: Path, capabilities: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "capability_id", "observed_on_raw_ready", "parse_error", "complexity", "source_ability_count",
        "monster_count", "ready_monster_count", "blocked_monster_count", "mechanics", "sections",
        "source_names", "exact_fingerprints", "ready_monsters", "blocked_monsters",
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in sorted(
            capabilities,
            key=lambda item: (
                bool(item["parse_error"]),
                -int(item["blocked_monster_count"]),
                not bool(item["observed_on_raw_ready"]),
                int(item["complexity"]),
                str(item["capability_id"]),
            ),
        ):
            row = dict(record)
            for field in ("mechanics", "sections", "source_names", "exact_fingerprints", "ready_monsters", "blocked_monsters"):
                row[field] = " | ".join(record[field])
            writer.writerow({field: row[field] for field in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description="Group all SRD monsters and source abilities by normalized combat math.")
    parser.add_argument("--csv", type=Path, help="Optional Excel-friendly monster matrix CSV output path.")
    parser.add_argument("--ability-csv", type=Path, help="Optional source-ability equivalence CSV output path.")
    parser.add_argument("--capability-csv", type=Path, help="Optional reusable capability-family CSV output path.")
    args = parser.parse_args()
    records = _records()
    abilities = _ability_records()
    capabilities = _capability_records(abilities)
    blocked = [record for record in records if not record["ready"] and not record["ignored_noncombat"]]
    families: dict[str, list[str]] = defaultdict(list)
    mechanics: dict[str, list[str]] = defaultdict(list)
    for record in blocked:
        families[str(record["fingerprint"])].append(str(record["monster"]))
        for mechanic in record["mechanics"]:
            mechanics[str(mechanic)].append(str(record["monster"]))

    print(
        "MONSTER_MATRIX_BASELINE"
        f"\ttotal={len(records)}"
        f"\tready={sum(bool(record['ready']) for record in records)}"
        f"\tblocked={len(blocked)}"
        f"\tignored_noncombat={sum(bool(record['ignored_noncombat']) for record in records)}"
        f"\tfingerprints={len(families)}"
        f"\tsource_abilities={len(abilities)}"
        f"\tcapability_families={len(capabilities)}"
        f"\tparse_errors={sum(bool(record['parse_error']) for record in abilities)}"
    )
    for mechanic, names in sorted(mechanics.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"MONSTER_MATRIX_MECHANIC\t{mechanic}\t{len(names)}\t" + " | ".join(sorted(names)))
    for fingerprint, names in sorted(families.items(), key=lambda item: (-len(item[1]), item[0]))[:_FAMILY_LIMIT]:
        print(f"MONSTER_MATRIX_FAMILY\t{len(names)}\t{fingerprint}\t" + " | ".join(sorted(names)))
    for capability in sorted(
        capabilities,
        key=lambda item: (-int(item["blocked_monster_count"]), not bool(item["observed_on_raw_ready"]), int(item["complexity"])),
    )[:_FAMILY_LIMIT]:
        print(
            f"MONSTER_ABILITY_FAMILY\tblocked={capability['blocked_monster_count']}"
            f"\tready={capability['ready_monster_count']}\t{capability['capability_id']}"
            f"\tnames=" + " | ".join(capability["source_names"])
        )
    for rank, record in enumerate(sorted(blocked, key=_queue_key)[:_QUEUE_LIMIT], start=1):
        blockers = "+".join(record["unsupported_families"]) or "none"
        mechanics_label = "+".join(record["mechanics"]) or "combat-math-none"
        print(
            f"MONSTER_MATRIX_QUEUE\t{rank}\t{record['monster']}"
            f"\tunsupported={record['unsupported_count']}\tcomplexity={record['complexity']}"
            f"\tedge={str(record['edge_case']).lower()}\tblockers={blockers}\tmechanics={mechanics_label}"
        )
    if args.csv:
        _write_csv(args.csv, records)
        print(f"MONSTER_MATRIX_CSV\t{args.csv}")
    if args.ability_csv:
        _write_ability_csv(args.ability_csv, abilities)
        print(f"MONSTER_ABILITY_CSV\t{args.ability_csv}")
    if args.capability_csv:
        _write_capability_csv(args.capability_csv, capabilities)
        print(f"MONSTER_CAPABILITY_CSV\t{args.capability_csv}")


if __name__ == "__main__":
    main()
