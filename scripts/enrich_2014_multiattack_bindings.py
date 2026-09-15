from __future__ import annotations

import argparse
import json
import logging
import re
import unicodedata
from pathlib import Path

from import_2014_multiattack import parse_multiattack

logger = logging.getLogger(__name__)


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def enrich_catalog(source_path: Path, catalog_path: Path) -> int:
    """Persist parsed Multiattack policy/binding metadata without changing runtime semantics."""
    try:
        source_rows = json.loads(source_path.read_text(encoding="utf-8"))
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        source_by_id = {_slug(row["name"]): row for row in source_rows}
        enriched = 0
        for monster in catalog:
            source = source_by_id.get(monster["id"])
            if source is None:
                raise ValueError(f"Missing pinned source row for {monster['id']}.")
            parsed = parse_multiattack(source.get("Actions"), monster.get("attacks", []))
            monster["multiattack_policy"] = parsed.get("policy") if parsed else None
            monster["multiattack_binding"] = parsed.get("binding") if parsed else None
            if parsed and parsed.get("slots"):
                monster["multiattack_slots"] = parsed["slots"]
            if monster["multiattack_binding"] is not None:
                enriched += 1
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"bound unresolved Multiattack structures for {enriched} 2014 monsters")
        return enriched
    except Exception:
        logger.exception("Failed to enrich 2014 Multiattack bindings in %s.", catalog_path)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist source-faithful 2014 Multiattack bindings.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        enrich_catalog(args.source, args.catalog)
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    raise SystemExit(main())
