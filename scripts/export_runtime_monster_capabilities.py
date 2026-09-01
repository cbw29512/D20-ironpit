from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.capability_from_template import definition_from_template
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")


def main() -> None:
    try:
        monsters = build_arena_roster().monsters
        definitions = [definition_from_template(monster) for monster in monsters]
        ids = [definition.id for definition in definitions]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Runtime monster ids must be unique before capability export.")
        payload = [definition.model_dump(mode="json", exclude_none=True) for definition in definitions]
        _OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        logger.info("Exported %d runtime monster capability definitions to %s.", len(payload), _OUTPUT)
        print(f"Exported {len(payload)} runtime monster capability definitions to {_OUTPUT}.")
    except Exception:
        logger.exception("Runtime monster capability export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
