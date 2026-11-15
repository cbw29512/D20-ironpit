"""Read-only, full-cohort 2014 spellcasting gap report.

Run from repo root: PYTHONPATH=backend python scripts/report_spellcaster_gaps_2014.py
No source cards, combat state, generated artifacts, or manifests are modified.
"""
from __future__ import annotations

from collections import defaultdict
import json
import logging
from pathlib import Path

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_prepared_spells_2014 import supports_prepared_spellcasting_2014
from spellcaster_audit_2014 import blocked_caster_names, innate_spell_gap, prepared_spell_gap

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


def build_report() -> dict:
    try:
        names = blocked_caster_names(ROOT / "docs/MONSTER_BLOCKERS_2014.md")
        cards = {card.name: card for card in load_monster_source_2014()}
        rows = []
        missing_owners = defaultdict(list)
        for name in names:
            card = cards[name]
            if card.spellcasting and card.innate_spellcasting:
                raise ValueError(f"{name} declares both prepared and innate spellcasting")
            if card.spellcasting:
                item = prepared_spell_gap(card)
                assert not supports_prepared_spellcasting_2014(card), name
            elif card.innate_spellcasting:
                item = innate_spell_gap(card)
                assert not supports_innate_spellcasting_2014(card), name
            else:
                raise ValueError(f"{name} has spellcasting blocker without source spell list")
            item["monster"] = name
            item["other_blockers"] = "see generated MONSTER_BLOCKERS_2014.md"
            for spell in item["unbound"]:
                missing_owners[spell].append(name)
            rows.append(item)
        return {
            "source": "generated 2014 monster blockers + immutable 327-card corpus",
            "blocked_casters": len(rows),
            "unique_unbound_spells": len(missing_owners),
            "missing_spells_by_reuse": [
                {"spell": spell, "caster_count": len(owners), "casters": sorted(owners)}
                for spell, owners in sorted(
                    missing_owners.items(), key=lambda kv: (-len(kv[1]), kv[0])
                )
            ],
            "casters": rows,
        }
    except Exception:
        logger.exception("Full 2014 spellcaster audit failed closed")
        raise


def main() -> None:
    try:
        data = build_report()
        print("IRON_PIT_2014_SPELLCASTER_AUDIT_BEGIN")
        print(json.dumps(data, indent=2, sort_keys=True))
        print("IRON_PIT_2014_SPELLCASTER_AUDIT_END")
    except Exception:
        logger.exception("Could not report complete 2014 spellcaster audit")
        raise


if __name__ == "__main__":
    main()
