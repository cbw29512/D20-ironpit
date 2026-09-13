from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12,
    "twenty": 20, "twenty-four": 24,
}
_TRAIT = re.compile(r"<strong>(?P<name>[^<]+?)\.?\s*</strong>\s*(?P<body>.*)", re.I | re.S)
_POOL = re.compile(
    r"\bhas\s+(?P<count>\d+|[a-z-]+)\s+(?P<ammo>[a-z][a-z -]+?)\.\s*"
    r"Used\s+(?P<used>[a-z][a-z -]+?)\s+regrow\s+when\b.*?finishes\s+a\s+long\s+rest",
    re.I | re.S,
)


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _singular(value: str) -> str:
    clean = value.strip().lower()
    return clean[:-1] if clean.endswith("s") else clean


def parse_regrowing_ammunition(paragraph: str) -> tuple[str, str, int] | None:
    trait = _TRAIT.search(paragraph)
    if trait is None:
        return None
    pool = _POOL.search(trait.group("body"))
    if pool is None:
        return None
    token = pool.group("count").lower()
    count = int(token) if token.isdigit() else _NUMBER_WORDS.get(token)
    if count is None:
        return None
    ammo = _singular(pool.group("ammo"))
    used = _singular(pool.group("used"))
    if ammo != used:
        return None
    return trait.group("name").rstrip("."), _key(ammo), count


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich finite 2014 attack ammunition from pinned trait text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}
        parsed_count = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None:
                continue
            for paragraph in re.findall(r"<p>(.*?)</p>", raw.get("Traits", ""), re.I | re.S):
                parsed = parse_regrowing_ammunition(paragraph)
                if parsed is None:
                    continue
                trait_name, action_id, count = parsed
                if action_id not in {attack["id"] for attack in row.get("attacks", [])}:
                    continue
                row.setdefault("limited_action_uses", {})[action_id] = count
                row.setdefault("data_bound_trait_names", []).append(trait_name)
                parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} finite attack ammunition pools")
        return 0
    except Exception as exc:
        logger.exception("2014 attack resource enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
