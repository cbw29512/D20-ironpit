from __future__ import annotations

import json
import logging
from pathlib import Path

from export_browser_heroes import main as export_browser_heroes

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "backend" / "app" / "content" / "data"
SOURCE = DATA / "srd_5_2_1_monsters.json"
CORRECTIONS = DATA / "srd_5_2_1_monster_corrections.json"
DESTINATION = ROOT / "frontend" / "data" / "srd_5_2_1_monsters.json"


def _prepare_monster_catalog() -> None:
    try:
        rows = json.loads(SOURCE.read_text(encoding="utf-8"))
        corrections = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) != 328:
            raise RuntimeError("Expected known 328-record parser base before corrections.")
        if not isinstance(corrections, list) or len(corrections) != 2:
            raise RuntimeError("Expected exactly two SRD parser correction records.")
        combined = [*rows, *corrections]
        ids = {str(row["id"]) for row in combined}
        names = {str(row["name"]) for row in combined}
        if len(combined) != 330 or len(ids) != 330 or len(names) != 330:
            raise RuntimeError("Static SRD monster catalog must contain 330 unique records.")
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        DESTINATION.write_text(json.dumps(combined, separators=(",", ":")), encoding="utf-8")
        logger.info("Prepared 330 SRD monsters for static browser delivery.")
    except Exception:
        logger.exception("Static SRD monster preparation failed.")
        raise


def main() -> None:
    try:
        _prepare_monster_catalog()
        export_browser_heroes()
        logger.info("Static Iron Pit content preparation completed.")
    except Exception:
        logger.exception("Static Iron Pit content preparation failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
