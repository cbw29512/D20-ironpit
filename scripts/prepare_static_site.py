from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_catalog import load_monster_rows
from export_browser_heroes import main as export_browser_heroes
from export_browser_monsters import main as export_browser_monsters
from export_figure_profiles import main as export_figure_profiles

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "data" / "srd_5_2_1_monsters.json"


def _prepare_monster_catalog() -> None:
    """Export the exact canonical SRD rows already used by Python certification."""
    try:
        rows = load_monster_rows()
        if len(rows) != 330:
            raise RuntimeError("Static SRD monster catalog must contain 330 canonical records.")
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        DESTINATION.write_text(json.dumps(rows, separators=(",", ":")), encoding="utf-8")
        logger.info("Prepared 330 canonical SRD monsters for static browser delivery.")
    except Exception:
        logger.exception("Static SRD monster preparation failed.")
        raise


def main() -> None:
    try:
        _prepare_monster_catalog()
        export_browser_heroes()
        export_browser_monsters()
        export_figure_profiles()
        logger.info("Static Iron Pit content preparation completed.")
    except Exception:
        logger.exception("Static Iron Pit content preparation failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
