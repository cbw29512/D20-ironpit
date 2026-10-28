"""Scan all 327 cards for source-declared innate Magic Missile behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_MAGIC_MISSILE_BINDINGS_2014.json"

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_auto_hit_spell_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_spell_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "magic-missile"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Magic Missile rows"})
            continue
        row = declared[0]
        actions = [item for item in innate_auto_hit_spell_actions_2014(card) if item.id == "magic-missile"]
        grants = [item for item in innate_alternate_spell_casts_2014(card) if item.spell_id == "magic-missile"]
        resources = {item.id for item in innate_spell_resources_2014(card)}
        if len(actions) != 1 or len(grants) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action, grant = actions[0], grants[0]
        if (
            row.get("usage") != "at_will" or row.get("uses_per_day") is not None
            or action.level != 1 or action.action_cost != "action" or action.range_ft != 120
            or action.projectile_count != 3 or action.projectiles_per_slot_above != 1
            or action.damage_dice_count != 1 or action.damage_dice_size != 4
            or action.damage_bonus != 1 or action.damage_type != "force"
            or grant.cast_level != 1 or grant.resource_id is not None
            or "magic-missile" in resources
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action lost source/shared spell parameters"})
            continue
        python_wired.append(card.id)
        browser = template_row(compile_combatant(adapt_monster_mechanics_2014(card)))
        browser_actions = [item for item in browser.get("auto_hit_spell_actions", []) if item.get("id") == "magic-missile"]
        browser_grants = [item for item in browser.get("alternate_spell_cast_grants", []) if item.get("spell_id") == "magic-missile"]
        if (
            len(browser_actions) == 1 and len(browser_grants) == 1
            and browser_actions[0].get("range") == 120
            and browser_actions[0].get("projectileCount") == 3
            and browser_actions[0].get("damageDiceCount") == 1
            and browser_actions[0].get("damageDiceSize") == 4
            and browser_actions[0].get("damageBonus") == 1
            and browser_actions[0].get("damageType") == "force"
            and browser_grants[0].get("cast_level") == 1
            and browser_grants[0].get("resource_id") is None
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Magic Missile semantics"})
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "wired_python_card_count": len(python_wired),
        "wired_browser_card_count": len(browser_wired),
        "wired_cards": sorted(set(python_wired) & set(browser_wired)),
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: explicit exceptions remain",
    }


def render() -> str:
    return json.dumps(report(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is stale; regenerate with this script.")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
