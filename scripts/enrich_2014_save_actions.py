from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from import_2014_innate_spellcasting import parse_innate_spellcasting
from import_2014_multiattack import parse_multiattack
from import_2014_recharge import parse_action_recharges
from import_2014_save_actions import parse_save_actions
from import_2014_zero_hp_prevention import parse_zero_hp_prevention

logger = logging.getLogger(__name__)


def _bind_frightful_multiattack(row: dict, actions: str) -> None:
    save_ids = {action["id"] for action in row["saving_throw_actions"]}
    if "frightful-presence" not in save_ids:
        return
    multiattack = next((
        paragraph for paragraph in re.findall(r"<p>(.*?)</p>", actions or "", re.I | re.S)
        if re.search(r"<strong>\s*Multiattack", paragraph, re.I)
    ), "")
    if not re.search(r"can use (?:its )?Frightful Presence", multiattack, re.I):
        return
    slots = row.get("multiattack_slots") or []
    if not slots or any("frightful-presence" in slot for slot in slots):
        return
    row["multiattack_slots"] = [["frightful-presence"], *slots]


def _bind_multiattack_policy(row: dict, actions: str) -> None:
    parsed = parse_multiattack(actions, row.get("attacks") or [])
    if parsed is None:
        return
    row["multiattack_slots"] = parsed["slots"]
    row["multiattack_policy"] = parsed.get("policy")


def enrich(source_path: Path, catalog_path: Path) -> None:
    source_rows = json.loads(source_path.read_text(encoding="utf-8"))
    catalog_rows = json.loads(catalog_path.read_text(encoding="utf-8"))
    source_by_name = {row["name"]: row for row in source_rows}
    if len(source_by_name) != len(source_rows):
        raise ValueError("2014 source contains duplicate monster names.")
    for row in catalog_rows:
        source = source_by_name.get(row["name"])
        if source is None:
            raise ValueError(f"Missing pinned source row for {row['name']!r}.")
        traits = source.get("Traits", "")
        actions = source.get("Actions", "")
        recharges = parse_action_recharges(actions)
        row["saving_throw_actions"] = parse_save_actions(actions, recharges)
        row["innate_spellcasting"] = parse_innate_spellcasting(traits)
        row["zero_hp_prevention"] = parse_zero_hp_prevention(traits)
        _bind_multiattack_policy(row, actions)
        _bind_frightful_multiattack(row, actions)
    catalog_path.write_text(
        json.dumps(catalog_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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
