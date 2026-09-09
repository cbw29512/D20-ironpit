from __future__ import annotations

import argparse
import difflib
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


def _strip_default_gate(effect: dict[str, object]) -> None:
    gate = effect.get("gate")
    if not isinstance(gate, dict):
        return
    if not gate.get("required_target_tags") and not gate.get("excluded_target_tags") \
            and not gate.get("excluded_creature_types") and not gate.get("save_ability"):
        effect.pop("gate", None)


def _registry_row(definition) -> dict[str, object]:
    row = definition.model_dump(
        mode="json",
        exclude_none=True,
        exclude={"progression_features": _HERO_ONLY_PROGRESSION_FIELDS},
    )
    row.pop("creature_type", None)
    if not row.get("creature_tags"):
        row.pop("creature_tags", None)
    for action in [*row.get("attacks", []), *row.get("save_actions", [])]:
        if action.get("resource_id") is None and action.get("resource_cost") == 1:
            action.pop("resource_cost", None)
        for effect in action.get("effects", []):
            if isinstance(effect, dict):
                _strip_default_gate(effect)
    for action in row.get("save_actions", []):
        if not action.get("effects"):
            action.pop("effects", None)
    return row


def render_registry() -> str:
    monsters = build_legacy_monster_templates()
    definitions = [definition_from_template(monster) for monster in monsters]
    ids = [definition.id for definition in definitions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Legacy runtime monster ids must be unique before capability export.")
    return json.dumps([_registry_row(item) for item in definitions], indent=2, sort_keys=False) + "\n"


def _stale_diff(current: str, rendered: str) -> str:
    lines = list(difflib.unified_diff(
        current.splitlines(), rendered.splitlines(), fromfile=str(_OUTPUT), tofile="generated", lineterm="",
    ))
    return "\n".join(lines[:160])


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the legacy monster runtime into capability data.")
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in registry is stale.")
    args = parser.parse_args()
    try:
        rendered = render_registry()
        if args.check:
            current = _OUTPUT.read_text(encoding="utf-8") if _OUTPUT.exists() else ""
            if current != rendered:
                logger.error("Combat capability registry diff:\n%s", _stale_diff(current, rendered))
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
