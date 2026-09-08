from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.content.capability_from_template import definition_from_template
from app.content.legacy_monster_roster import build_legacy_monster_templates

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")
_HERO_ONLY_PROGRESSION_FIELDS = {
    "danger_sense", "reckless_attack", "frenzy", "fast_movement_bonus_ft", "mindless_rage",
    "instinctive_pounce_fraction", "great_weapon_fighting", "indomitable_bonus",
    "tactical_master_sap_weapon_ids", "sneak_attack_d6",
}


def render_registry() -> str:
    monsters = build_legacy_monster_templates()
    definitions = [definition_from_template(monster) for monster in monsters]
    ids = [definition.id for definition in definitions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Runtime monster ids must be unique before capability export.")
    payload = [
        definition.model_dump(
            mode="json",
            exclude_none=True,
            exclude={"progression_features": _HERO_ONLY_PROGRESSION_FIELDS},
        )
        for definition in definitions
    ]
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def sync_registry() -> bool:
    """Write the deterministic derived registry and return whether it changed."""
    rendered = render_registry()
    current = _OUTPUT.read_text(encoding="utf-8") if _OUTPUT.exists() else None
    if current == rendered:
        return False
    _OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    _OUTPUT.write_text(rendered, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the derived monster capability registry.")
    parser.add_argument("--check", action="store_true", help="Synchronize and verify deterministic generation for CI compatibility.")
    args = parser.parse_args()
    try:
        changed = sync_registry()
        count = len(json.loads(_OUTPUT.read_text(encoding="utf-8")))
        state = "refreshed" if changed else "current"
        print(f"Capability registry {state}: {_OUTPUT} ({count} monsters).")
        if not args.check:
            logger.info("Capability registry %s with %d definitions.", state, count)
    except Exception:
        logger.exception("Runtime monster capability export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
