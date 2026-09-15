from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_swallow_actions import (
    parse_grapple_containment_action,
    parse_on_hit_swallow_attack,
    parse_swallow_action,
)

logger = logging.getLogger(__name__)


def _parse_swallow_from_actions(actions: str) -> dict | None:
    paragraphs = re.findall(r"<p>(.*?)</p>", actions or "", re.I | re.S)
    for index, paragraph in enumerate(paragraphs):
        direct = parse_grapple_containment_action(paragraph)
        if direct is not None:
            return direct
        candidates = [paragraph]
        if index + 1 < len(paragraphs):
            candidates.append(f"{paragraph} {paragraphs[index + 1]}")
        for candidate in candidates:
            parsed = parse_swallow_action(candidate) or parse_on_hit_swallow_attack(candidate)
            if parsed is not None:
                return parsed
    return None


def _bind_on_hit_swallow(row: dict, parsed: dict) -> dict:
    ability = parsed.pop("on_hit_save_ability", None)
    dc = parsed.pop("on_hit_save_dc", None)
    if ability is None and dc is None:
        return parsed
    if ability is None or dc is None:
        raise ValueError(f"Incomplete save-triggered Swallow data for {row['name']}.")
    attack_id = parsed.get("attack_id")
    if attack_id is None:
        raise ValueError(f"Save-triggered Swallow is missing an attack id for {row['name']}.")
    attack = next((item for item in row.get("attacks", []) if item.get("id") == attack_id), None)
    if attack is None:
        raise ValueError(f"Swallow attack {attack_id!r} is missing for {row['name']}.")
    if attack.get("on_hit_save_effect") is not None:
        raise ValueError(f"Swallow attack {attack_id!r} already has a save rider for {row['name']}.")
    attack["on_hit_save_effect"] = {
        "save_ability": ability, "dc": dc,
        "max_target_size": parsed["max_target_size"], "swallow_on_failure": True,
    }
    attack["source_complete"] = True
    attack["unsupported_text"] = None
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 containment actions from pinned source text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}; parsed_count = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None:
                continue
            parsed = _parse_swallow_from_actions(raw.get("Actions", ""))
            if parsed is None:
                continue
            row["swallow_actions"] = [_bind_on_hit_swallow(row, parsed)]
            parsed_count += 1
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed_count} containment actions")
        return 0
    except Exception as exc:
        logger.exception("2014 containment enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
