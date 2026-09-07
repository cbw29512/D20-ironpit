from __future__ import annotations

import argparse
import csv
import io
import json
import re
from fractions import Fraction
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_mechanic_fingerprint import (
    mechanic_equivalence_fingerprint,
    mechanic_fingerprint,
    normalized_monster_mechanics,
    source_ability_records,
)
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _NONCOMBAT, _source_blockers

_ROOT = Path(__file__).resolve().parents[1]
_MASTER = _ROOT / "data/monster_master_ledger.json"
_ACTIVE_JSON = _ROOT / "data/monster_active_queue.json"
_ACTIVE_CSV = _ROOT / "data/monster_active_queue.csv"
_STATS = re.compile(
    r"\bStr\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)\s+Dex\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)\s+"
    r"Con\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)\s+Int\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)\s+"
    r"Wis\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)\s+Cha\s+(\d+)\s+([+-]\d+)\s+([+-]\d+)",
    re.I,
)
_INITIATIVE = re.compile(r"\bInitiative\s+([+-]?\d+)", re.I)


def _cr(challenge: object) -> str:
    return str(challenge).split(" ", 1)[0]


def _sort_key(row: dict[str, object]) -> tuple[Fraction, str]:
    return Fraction(_cr(row["challenge"])), str(row["name"])


def _ability_stats(raw: str) -> dict[str, dict[str, int]]:
    match = _STATS.search(raw)
    if match is None:
        return {}
    values = match.groups()
    result: dict[str, dict[str, int]] = {}
    for index, name in enumerate(("str", "dex", "con", "int", "wis", "cha")):
        offset = index * 3
        result[name] = {"score": int(values[offset]), "mod": int(values[offset + 1]), "save": int(values[offset + 2])}
    return result


def _build_records() -> list[dict[str, object]]:
    rows = sorted(load_monster_rows(), key=_sort_key)
    names = {str(row["name"]) for row in rows}
    cards = {card.name: card for card in build_monster_catalog()}
    records: list[dict[str, object]] = []
    for row in rows:
        name = str(row["name"])
        card = cards[name]
        ready = card.coverage_status is CoverageStatus.RAW_READY
        blockers = [] if ready else _source_blockers(row, names)
        status = "ready" if ready else "blocked"
        if blockers == [_NONCOMBAT]:
            status, blockers = "deferred_noncombat", []
        elif not ready and not blockers:
            blockers = ["unclassified-source-audit-gap"]
        mechanics = normalized_monster_mechanics(row)
        raw = str(row.get("rawText", ""))
        initiative = _INITIATIVE.search(raw)
        records.append({
            "id": str(row["id"]), "name": name, "cr": _cr(row["challenge"]),
            "status": status, "ready": ready, "runnable_template_id": card.runnable_template_id,
            "blockers": sorted(set(blockers)), "mechanics": mechanics,
            "mechanic_fingerprint": mechanic_fingerprint(row),
            "equivalence_fingerprint": mechanic_equivalence_fingerprint(mechanics),
            "initiative_bonus": int(initiative.group(1)) if initiative else None,
            "ability_stats": _ability_stats(raw), "abilities": source_ability_records(row), "source": dict(row),
        })
    if len(records) != 330 or len({str(record["id"]) for record in records}) != 330:
        raise RuntimeError("Monster work ledger must contain exactly 330 unique SRD monsters.")
    return records


def _payload(records: list[dict[str, object]]) -> str:
    statuses = ("ready", "blocked", "deferred_noncombat")
    counts = {status: sum(record["status"] == status for record in records) for status in statuses}
    return json.dumps({"total": len(records), "counts": counts, "records": records}, ensure_ascii=False, indent=2) + "\n"


def _active_csv(records: list[dict[str, object]]) -> str:
    fields = (
        "cr", "name", "type", "size", "alignment", "armor_class", "hit_points", "speed",
        "initiative_bonus", "ability_stats", "blockers", "mechanics", "ability_names", "traits", "actions",
        "bonus_actions", "reactions", "legendary_actions", "raw_text", "source_reference",
    )
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        source = record["source"]
        abilities = record["abilities"]
        writer.writerow({
            "cr": record["cr"], "name": record["name"], "type": source.get("type", ""),
            "size": source.get("size", ""), "alignment": source.get("alignment", ""),
            "armor_class": source.get("armorClass", ""), "hit_points": source.get("hitPoints", ""),
            "speed": source.get("speed", ""), "initiative_bonus": record["initiative_bonus"],
            "ability_stats": json.dumps(record["ability_stats"], separators=(",", ":")),
            "blockers": " | ".join(record["blockers"]), "mechanics": " | ".join(record["mechanics"]),
            "ability_names": " | ".join(f"{item['section']}:{item['source_name']}" for item in abilities),
            "traits": source.get("traits", ""), "actions": source.get("actions", ""),
            "bonus_actions": source.get("bonusActions", ""), "reactions": source.get("reactions", ""),
            "legendary_actions": source.get("legendaryActions", ""), "raw_text": source.get("rawText", ""),
            "source_reference": source.get("sourceReference", ""),
        })
    return handle.getvalue()


def _sync(path: Path, expected: str, check: bool) -> None:
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            raise RuntimeError(f"Generated monster work ledger is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export complete SRD monster ledger and blocked-only CR work queue.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = _build_records()
    active = [record for record in records if record["status"] == "blocked"]
    if any(record["ready"] for record in active):
        raise RuntimeError("Ready monsters must never remain in the active work queue.")
    _sync(_MASTER, _payload(records), args.check)
    _sync(_ACTIVE_JSON, _payload(active), args.check)
    _sync(_ACTIVE_CSV, _active_csv(active), args.check)
    print(f"MONSTER_WORK_LEDGER\ttotal={len(records)}\tready={sum(record['ready'] for record in records)}\tactive={len(active)}")


if __name__ == "__main__":
    main()
