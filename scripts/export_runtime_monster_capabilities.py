from __future__ import annotations

import argparse
import difflib
import json
import logging
from pathlib import Path

from app.content.capability_from_template import definition_from_template
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_creature_types import complete_monster_creature_types

logger = logging.getLogger(__name__)
_OUTPUT = Path("backend/app/content/data/combatant_capabilities_v1.json")
_HERO_ONLY_PROGRESSION_FIELDS = {
    "danger_sense", "reckless_attack", "frenzy", "frenzy_bonus_attack_2014", "intimidating_presence_2014_dc",
    "brutal_critical_dice", "fast_movement_bonus_ft", "mindless_rage", "instinctive_pounce_fraction",
    "great_weapon_fighting", "indomitable_reroll", "indomitable_bonus", "tactical_master_sap_weapon_ids",
    "sneak_attack_d6", "uncanny_dodge", "evasion",
    "martial_arts_bonus_attack", "martial_arts_die_size", "flurry_of_blows", "deflect_missiles",
    "open_hand_technique", "stunning_strike", "divine_smite_2014", "turn_unholy_2014",
    "aura_of_protection_2014_bonus", "aura_radius_2014_ft", "aura_of_devotion_2014", "aura_of_courage_2014",
    "sacred_weapon_2014_bonus", "survivor_heal_amount", "resource_backed_d20_bonus_dice",
}



def _strip_extension_defaults(value):
    """Keep generated monster capability JSON stable for unused extension fields."""
    if isinstance(value, list):
        return [_strip_extension_defaults(item) for item in value]
    if not isinstance(value, dict):
        return value
    cleaned = {}
    for key, item in value.items():
        if key == "replacement_hp" and item == 0:
            continue
        if key == "minimum_value" and item == 0:
            continue
        if key == "prevents_instant_death" and item is False:
            continue
        if key in {"effect_tags", "required_effect_tags", "failed_save_modifier_effects"} and item == []:
            continue
        if key == "replacement_form_actions" and item == []:
            continue
        cleaned[key] = _strip_extension_defaults(item)
    return cleaned


def render_registry() -> str:
    try:
        monsters = complete_monster_creature_types(
            build_legacy_monster_templates(include_capability_migrated=False)
        )
        definitions = [definition_from_template(monster) for monster in monsters]
        ids = [definition.id for definition in definitions]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Legacy runtime monster ids must be unique before capability export.")
        payload = [
            _strip_extension_defaults(definition.model_dump(
                mode="json",
                exclude_none=True,
                exclude={"progression_features": _HERO_ONLY_PROGRESSION_FIELDS, "effect_removal_actions": True},
            ))
            for definition in definitions
        ]
        return json.dumps(payload, indent=2, sort_keys=False) + "\n"
    except Exception:
        logger.exception("Failed to render runtime monster capability registry.")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the legacy monster runtime into capability data.")
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in registry is stale.")
    args = parser.parse_args()
    try:
        rendered = render_registry()
        if args.check:
            current = _OUTPUT.read_text(encoding="utf-8") if _OUTPUT.exists() else ""
            if current != rendered:
                diff = difflib.unified_diff(
                    current.splitlines(),
                    rendered.splitlines(),
                    fromfile=str(_OUTPUT),
                    tofile="fresh-runtime-capabilities",
                    lineterm="",
                )
                for line in list(diff)[:160]:
                    print(line)
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
