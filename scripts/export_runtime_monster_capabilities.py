from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.content.capability_from_template import definition_from_template
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.domain.capabilities import CombatantDefinition

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")
_HERO_ONLY_PROGRESSION_FIELDS = {
    "danger_sense", "reckless_attack", "frenzy", "fast_movement_bonus_ft", "mindless_rage",
    "instinctive_pounce_fraction", "great_weapon_fighting", "indomitable_bonus",
    "tactical_master_sap_weapon_ids", "sneak_attack_d6",
}


def _definition_payload(definition: CombatantDefinition) -> dict[str, object]:
    """Serialize one legacy definition without emitting empty/default optional capability families."""
    try:
        payload = definition.model_dump(
            mode="json",
            exclude_none=True,
            exclude={"progression_features": _HERO_ONLY_PROGRESSION_FIELDS},
        )
        if not definition.attack_roll_advantage_triggers: payload.pop("attack_roll_advantage_triggers", None)
        if not definition.saving_throw_advantage_triggers: payload.pop("saving_throw_advantage_triggers", None)
        for attack in payload.get("attacks", []):
            if isinstance(attack, dict) and not attack.get("resource_id"): attack.pop("resource_cost", None)
        for action in payload.get("save_actions", []):
            if isinstance(action, dict) and not action.get("magical"): action.pop("magical", None)
        return payload
    except Exception:
        logger.exception("Failed to serialize legacy capability definition %s.", definition.id)
        raise


def render_registry() -> str:
    monsters = build_legacy_monster_templates()
    definitions = [definition_from_template(monster) for monster in monsters]
    ids = [definition.id for definition in definitions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Legacy runtime monster ids must be unique before capability export.")
    payload = [_definition_payload(definition) for definition in definitions]
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
