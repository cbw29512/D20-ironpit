from __future__ import annotations

import argparse
import json
from pathlib import Path

from import_2014_spellcasting import parse_spellcasting


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich canonical 2014 catalog with regular spellcasting data.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    source_rows = {row["name"]: row for row in json.loads(args.source.read_text(encoding="utf-8"))}
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    for monster in catalog:
        source = source_rows[monster["name"]]
        monster["spellcasting"] = parse_spellcasting(source.get("Traits"))
    args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"enriched regular spellcasting for {len(catalog)} 2014 monsters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
