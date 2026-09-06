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
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in sorted(records, key=_matrix_key):
            row = dict(record)
            row["work_rank"] = rank_by_name.get(str(record["monster"]), "")
            row["unsupported_families"] = " | ".join(record["unsupported_families"])
            row["mechanics"] = " | ".join(record["mechanics"])
            writer.writerow({field: row[field] for field in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description="Group all SRD monsters by normalized combat math.")
    parser.add_argument("--csv", type=Path, help="Optional Excel-friendly CSV output path.")
    args = parser.parse_args()
    records = _records()
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
    )
    for mechanic, names in sorted(mechanics.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"MONSTER_MATRIX_MECHANIC\t{mechanic}\t{len(names)}\t" + " | ".join(sorted(names)))
    for fingerprint, names in sorted(families.items(), key=lambda item: (-len(item[1]), item[0]))[:_FAMILY_LIMIT]:
        print(f"MONSTER_MATRIX_FAMILY\t{len(names)}\t{fingerprint}\t" + " | ".join(sorted(names)))
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


if __name__ == "__main__":
    main()
