from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_SURPRISE = re.compile(
    r"<strong>\s*Surprise Attack\.?\s*</strong>.*?extra\s+\d+\s*\((\d+)d(\d+)\)\s+damage",
    re.I | re.S,
)


def enrich_monster(monster: dict) -> bool:
    """Bind source Surprise Attack to a generic round-one initiative-lead damage trigger."""
    try:
        if "Surprise Attack" not in monster.get("trait_names", []):
            return False
        match = _SURPRISE.search(monster.get("source_traits") or "")
        if match is None:
            return False
        dice_count, dice_size = map(int, match.groups())
        changed = False
        for attack in monster.get("attacks", []):
            damage_type = (attack.get("damage") or {}).get("type")
            if damage_type is None:
                continue
            riders = attack.setdefault("conditional_damage", [])
            if any(item.get("trigger") == "round1_initiative_lead" for item in riders):
                continue
            if riders:
                raise ValueError(f"{monster['name']} {attack['name']} already has conditional damage.")
            riders.append({
                "trigger": "round1_initiative_lead",
                "mode": "add",
                "dice_count": dice_count,
                "dice_size": dice_size,
                "damage_bonus": 0,
                "damage_type": damage_type,
            })
            changed = True
        if changed:
            bound = monster.setdefault("data_bound_trait_names", [])
            if "Surprise Attack" not in bound:
                bound.append("Surprise Attack")
        return changed
    except Exception:
        logger.exception("Failed to enrich opening initiative damage for %s.", monster.get("name"))
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind 2014 opening initiative damage traits.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        rows = json.loads(args.catalog.read_text(encoding="utf-8"))
        count = sum(int(enrich_monster(row)) for row in rows)
        args.catalog.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {count} opening initiative damage monsters")
        return 0
    except Exception as exc:
        logger.exception("2014 opening initiative enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
