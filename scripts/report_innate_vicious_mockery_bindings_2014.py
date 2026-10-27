"""Scan all 327 cards for source-declared innate Vicious Mockery behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_VICIOUS_MOCKERY_BINDINGS_2014.json"

from app.content.monster_innate_source_2014 import innate_spell_save_dc_2014, innate_spells_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _spell


def report() -> dict:
    cards = load_monster_source_2014()
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "vicious-mockery"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Vicious Mockery rows"})
            continue
        row = declared[0]
        actions = [action for action in innate_spell_save_actions_2014(card) if action.id == "vicious-mockery"]
        dc = innate_spell_save_dc_2014(card)
        resources = {item.id for item in innate_spell_resources_2014(card)}
        if len(actions) != 1:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action = actions[0]
        effect = action.failed_save_timed_effect
        if (
            row.get("usage") != "at_will" or row.get("uses_per_day") is not None
            or dc is None or action.dc != dc or "vicious-mockery" in resources
            or action.level != 0 or action.action_cost != "action" or action.range_ft != 60
            or action.save_ability != "wisdom" or action.damage_dice_count != 1
            or action.damage_dice_size != 4 or action.damage_type != "psychic"
            or action.success_damage != "none" or not action.requires_target_hearing
            or not action.requires_target_sight or effect is None
            or effect.effect_id != "vicious-mockery-disadvantage"
            or effect.expiry_timing != "target_turn_end" or not effect.next_attack_disadvantage
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action lost source/shared spell parameters"})
            continue
        python_wired.append(card.id)
        browser = _spell(action)
        browser_effect = browser.get("failedSaveTimedEffect") or {}
        if (
            browser.get("id") == "vicious-mockery" and browser.get("dc") == dc
            and browser.get("range") == 60 and browser.get("saveAbility") == "wisdom"
            and browser.get("damageDiceCount") == 1 and browser.get("damageDiceSize") == 4
            and browser.get("damageType") == "psychic" and browser.get("successDamage") == "none"
            and browser.get("requiresTargetHearing") is True
            and browser.get("requiresTargetSight") is True
            and browser_effect.get("effectId") == "vicious-mockery-disadvantage"
            and browser_effect.get("expiryTiming") == "target_turn_end"
            and browser_effect.get("nextAttackDisadvantage") is True
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Vicious Mockery semantics"})
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
