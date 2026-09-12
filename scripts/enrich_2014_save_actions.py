from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_innate_spellcasting import parse_innate_spellcasting
from import_2014_legendary_actions import parse_legendary_actions
from import_2014_multiattack import parse_multiattack
from import_2014_recharge import parse_action_recharges
from import_2014_regeneration import parse_regeneration
from import_2014_save_actions import parse_save_actions
from import_2014_zero_hp_prevention import parse_zero_hp_prevention

logger = logging.getLogger(__name__)


def _bind_frightful_multiattack(row: dict, actions: str) -> None:
    save_ids = {action["id"] for action in row["saving_throw_actions"]}
    if "frightful-presence" not in save_ids: return
    multiattack = next((paragraph for paragraph in re.findall(r"<p>(.*?)</p>", actions or "", re.I | re.S) if re.search(r"<strong>\s*Multiattack", paragraph, re.I)), "")
    if not re.search(r"can use (?:its )?Frightful Presence", multiattack, re.I): return
    slots = row.get("multiattack_slots") or []
    if not slots or any("frightful-presence" in slot for slot in slots): return
    row["multiattack_slots"] = [["frightful-presence"], *slots]


def _bind_multiattack_policy(row: dict, actions: str) -> None:
    parsed = parse_multiattack(actions, row.get("attacks") or [])
    if parsed is None: return
    row["multiattack_slots"] = parsed["slots"]
    row["multiattack_policy"] = parsed.get("policy")


def _legendary_heading_key(name: str) -> str:
    clean = name.strip().rstrip(".")
    clean = re.sub(r"\s*\(Costs?\s+\d+\s+Actions?\)\s*", "", clean, flags=re.I)
    return clean.strip().lower()


def _bind_legendary_actions(row: dict, source_legendary_actions: str) -> None:
    uses, options, unsupported = parse_legendary_actions(
        source_legendary_actions,
        row.get("attacks") or [],
    )
    row["legendary_action_uses"] = uses
    row["legendary_actions"] = options
    # Preserve legendary_action_names as immutable source provenance. Runtime
    # certification uses a separate unsupported list so source fidelity can
    # compare every printed heading exactly. Cost suffixes are presentation,
    # while the typed option stores cost separately.
    supported = {_legendary_heading_key(option["name"]) for option in options}
    source_names = row.get("legendary_action_names") or []
    unresolved = [name for name in source_names if _legendary_heading_key(name) not in supported]
    unsupported_keys = {_legendary_heading_key(name) for name in unresolved}
    for name in unsupported:
        if _legendary_heading_key(name) not in unsupported_keys:
            unresolved.append(name)
            unsupported_keys.add(_legendary_heading_key(name))
    row["unsupported_legendary_action_names"] = unresolved


def enrich(source_path: Path, catalog_path: Path) -> None:
    source_rows = json.loads(source_path.read_text(encoding="utf-8"))
    catalog_rows = json.loads(catalog_path.read_text(encoding="utf-8"))
    source_by_name = {row["name"]: row for row in source_rows}
    if len(source_by_name) != len(source_rows): raise ValueError("2014 source contains duplicate monster names.")
    for row in catalog_rows:
        source = source_by_name.get(row["name"])
        if source is None: raise ValueError(f"Missing pinned source row for {row['name']!r}.")
        traits = source.get("Traits", ""); actions = source.get("Actions", "")
        recharges = parse_action_recharges(actions)
        row["saving_throw_actions"] = parse_save_actions(actions, recharges)
        row["innate_spellcasting"] = parse_innate_spellcasting(traits)
        row["zero_hp_prevention"] = parse_zero_hp_prevention(traits)
        row["regeneration"] = parse_regeneration(traits)
        _bind_multiattack_policy(row, actions)
        _bind_frightful_multiattack(row, actions)
        _bind_legendary_actions(row, source.get("Legendary Actions", ""))
    catalog_path.write_text(json.dumps(catalog_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Add typed 2014 combat action and trait data to a normalized catalog.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        enrich(args.source, args.catalog)
        print(f"enriched 2014 combat actions and trait profiles in {args.catalog}")
        return 0
    except Exception as exc:
        logger.exception("2014 action enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
