from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.content.capability_from_template import definition_from_template
from app.content.legacy_monster_roster import build_legacy_monster_templates

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")


def render_registry() -> str:
    monsters = build_legacy_monster_templates()
    definitions = [definition_from_template(monster) for monster in monsters]
    ids = [definition.id for definition in definitions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Legacy runtime monster ids must be unique before capability export.")
    payload = [definition.model_dump(mode="json", exclude_none=True) for definition in definitions]
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the legacy monster runtime into capability data.")
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in registry is stale.")
    args = parser.parse_args()
    try:
        rendered = render_registry()
        if args.check:
            if not _OUTPUT.exists() or _OUTPUT.read_text(encoding="utf-8") != rendered:
                raise RuntimeError("Combat capability registry is stale; regenerate it before committing.")
            print(f"Capability registry is deterministic and current: {_OUTPUT}.")
            return
        _OUTPUT.write_text(rendered, encoding="utf-8")
        count = len(json.loads(rendered))
        logger.info("Exported %d legacy monster capability definitions to %s.", count, _OUTPUT)
        print(f"Exported {count} legacy monster capability definitions to {_OUTPUT}.")
    except Exception:
        logger.exception("Runtime monster capability export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
