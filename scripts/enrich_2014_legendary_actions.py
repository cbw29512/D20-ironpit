from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.content.monster_catalog_2014_spells import SCOPED_OUT_NON_DAMAGE_SPELLS_2014
from import_2014_legendary_actions import parse_legendary_actions
from import_2014_spellcasting import parse_spellcasting

logger = logging.getLogger(__name__)


def _legendary_spellcasting_is_non_damage_only(source_traits: str | None) -> bool:
    """Return True when every prepared spell is outside the damage-first milestone."""
    try:
        profile = parse_spellcasting(source_traits)
        if not profile or not profile.get("source_complete") or not profile.get("spells"):
            return False
        return all(
            spell["id"] in SCOPED_OUT_NON_DAMAGE_SPELLS_2014
            for spell in profile["spells"]
        )
    except Exception as exc:
        logger.exception("Failed to classify legendary spellcasting scope: %s", exc)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 legendary actions from pinned source text.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        source = json.loads(args.source.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        by_name = {row["name"]: row for row in catalog}
        parsed_options = 0
        for raw in source:
            row = by_name.get(raw["name"])
            if row is None:
                continue
            uses, options, unsupported = parse_legendary_actions(
                raw.get("Legendary Actions"), row.get("attacks", [])
            )
            if (
                "Cast a Spell" in unsupported
                and _legendary_spellcasting_is_non_damage_only(raw.get("Traits"))
            ):
                unsupported = [name for name in unsupported if name != "Cast a Spell"]
            row["legendary_action_uses"] = uses
            row["legendary_actions"] = options
            row["unsupported_legendary_action_names"] = unsupported
            parsed_options += len(options)
        args.catalog.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"enriched {parsed_options} legendary action options")
        return 0
    except Exception as exc:
        logger.exception("2014 legendary action enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
