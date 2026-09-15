from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
import sys
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_OUTPUT = ROOT / "data" / "monsters" / "2014" / "certification_ledger.json"
sys.path.insert(0, str(BACKEND))

from app.content.monster_catalog_2014 import (  # noqa: E402
    compile_monster_2014,
    load_catalog_2014,
    unsupported_mechanics_2014,
)

logger = logging.getLogger(__name__)


class MonsterLedgerRow(TypedDict):
    id: str
    name: str
    status: str
    remaining_blocker_count: int
    remaining_blockers: list[str]


class LedgerPayload(TypedDict):
    schema_version: int
    ruleset: str
    catalog_count: int
    ready_count: int
    blocked_count: int
    blocker_families: dict[str, int]
    blocker_yield: dict[str, int]
    monsters: list[MonsterLedgerRow]


def _compile_blocker(monster: object) -> list[str]:
    try:
        compile_monster_2014(monster)  # type: ignore[arg-type]
        return []
    except Exception:
        logger.exception("Zero-blocker monster failed universal compile: %s", getattr(monster, "name", "unknown"))
        return ["compile:universal-runtime"]


def build_ledger() -> LedgerPayload:
    try:
        rows: list[MonsterLedgerRow] = []
        families: Counter[str] = Counter()
        blocker_owners: dict[str, set[str]] = defaultdict(set)
        for monster in load_catalog_2014():
            blockers = sorted(set(unsupported_mechanics_2014(monster)))
            if not blockers:
                blockers = _compile_blocker(monster)
            for blocker in blockers:
                families[blocker.split(":", 1)[0]] += 1
                blocker_owners[blocker].add(monster.id)
            rows.append({
                "id": monster.id,
                "name": monster.name,
                "status": "ready" if not blockers else "blocked",
                "remaining_blocker_count": len(blockers),
                "remaining_blockers": blockers,
            })
        rows.sort(key=lambda row: row["name"])
        ready = sum(row["status"] == "ready" for row in rows)
        yield_map = {key: len(value) for key, value in blocker_owners.items()}
        return {
            "schema_version": 1,
            "ruleset": "2014",
            "catalog_count": len(rows),
            "ready_count": ready,
            "blocked_count": len(rows) - ready,
            "blocker_families": dict(sorted(families.items(), key=lambda item: (-item[1], item[0]))),
            "blocker_yield": dict(sorted(yield_map.items(), key=lambda item: (-item[1], item[0]))),
            "monsters": rows,
        }
    except Exception as exc:
        logger.exception("Failed to build 2014 universal monster certification ledger.")
        raise RuntimeError("2014 monster certification ledger could not be built.") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Rescan every 2014 monster against the universal Iron Pit engine.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the committed ledger differs from a fresh full-roster scan.")
    args = parser.parse_args()
    try:
        payload = build_ledger()
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
                logger.error("2014 monster ledger is stale: %s", args.output)
                return 1
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(
            f"2014_MONSTER_LEDGER catalog={payload['catalog_count']} "
            f"ready={payload['ready_count']} blocked={payload['blocked_count']}"
        )
        return 0
    except Exception:
        logger.exception("2014 monster ledger export failed.")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    raise SystemExit(main())
