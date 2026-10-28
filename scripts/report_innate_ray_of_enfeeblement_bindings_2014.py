"""Scan all 327 cards for source-declared innate Ray of Enfeeblement behavior."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "INNATE_RAY_OF_ENFEEBLEMENT_BINDINGS_2014.json"

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_source_2014 import (
    innate_spell_save_dc_2014,
    innate_spellcasting_source_2014,
    innate_spells_2014,
)
from app.content.monster_innate_spells_2014 import innate_spell_attack_actions_2014
from app.content.monster_innate_support_2014 import innate_alternate_spell_casts_2014, innate_spell_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_catalog import load_monster_rows
from scripts.browser_template_serializer import template_row


def report() -> dict:
    cards = load_monster_source_2014()
    cards_2024 = load_monster_rows()
    applicable_2024 = []
    for card in cards_2024:
        source_text = (
            json.dumps(card, sort_keys=True).casefold().replace("-", " ").replace("_", " ")
        )
        if (
            "ray of enfeeblement" in source_text
            or (
                "strength-based" in source_text
                and "weapon" in source_text
                and ("half" in source_text or "halved" in source_text)
            )
        ):
            applicable_2024.append(str(card["id"]))
    applicable, python_wired, browser_wired, exceptions = [], [], [], []
    for card in cards:
        declared = [row for row in innate_spells_2014(card) if row.get("id") == "ray-of-enfeeblement"]
        if not declared:
            continue
        applicable.append(card.id)
        if len(declared) != 1:
            exceptions.append({"monster": card.id, "reason": "multiple innate Ray of Enfeeblement rows"})
            continue
        row = declared[0]
        source_casting = innate_spellcasting_source_2014(card) or {}
        source_attack_bonus = source_casting.get("attack_bonus")
        source_save_dc = innate_spell_save_dc_2014(card)
        source_uses = row.get("uses_per_day")
        if source_attack_bonus is None or source_save_dc is None or source_uses is None:
            exceptions.append({
                "monster": card.id,
                "reason": "source row lacks attack bonus, save DC, or daily use count",
            })
            continue
        actions = [item for item in innate_spell_attack_actions_2014(card) if item.id == "ray-of-enfeeblement"]
        grants = [item for item in innate_alternate_spell_casts_2014(card) if item.spell_id == "ray-of-enfeeblement"]
        resources = {item.id: item for item in innate_spell_resources_2014(card)}
        if len(actions) != 1 or len(grants) != 1 or "ray-of-enfeeblement" not in resources:
            exceptions.append({"monster": card.id, "reason": "source row did not compile exactly once"})
            continue
        action, grant = actions[0], grants[0]
        modifier, timed = action.on_hit_modifier_effects[0], action.on_hit_timed_effects[0]
        if (
            row.get("usage") != "per_day" or int(source_uses) <= 0
            or row.get("shared_pool") is not False or row.get("qualifier") is not None
            or action.level != 2 or action.range_ft != 60
            or action.attack_bonus != int(source_attack_bonus)
            or not action.concentration or action.duration_minutes != 1
            or modifier.kind != "weapon-attack-damage-multiplier" or modifier.multiplier != 0.5
            or modifier.required_attack_ability != "strength"
            or timed.repeat_save_ability != "constitution"
            or timed.repeat_save_dc != source_save_dc
            or timed.repeat_save_timing != "target_turn_end" or timed.duration_rounds != 10
            or grant.cast_level != 2 or grant.resource_id != "ray-of-enfeeblement"
            or resources["ray-of-enfeeblement"].max_uses != int(source_uses)
        ):
            exceptions.append({"monster": card.id, "reason": "compiled action lost source/shared spell parameters"})
            continue
        python_wired.append(card.id)
        browser = template_row(compile_combatant(adapt_monster_mechanics_2014(card)))
        browser_actions = [item for item in browser.get("spell_attack_actions", []) if item.get("id") == "ray-of-enfeeblement"]
        browser_grants = [item for item in browser.get("alternate_spell_cast_grants", []) if item.get("spell_id") == "ray-of-enfeeblement"]
        item = browser_actions[0] if len(browser_actions) == 1 else {}
        effect = (item.get("onHitModifierEffects") or [{}])[0]
        timed_row = (item.get("onHitTimedEffects") or [{}])[0]
        if (
            len(browser_actions) == 1 and len(browser_grants) == 1
            and item.get("range") == 60
            and item.get("attackBonus") == int(source_attack_bonus)
            and item.get("concentration") is True and item.get("durationMinutes") == 1
            and effect.get("kind") == "weapon-attack-damage-multiplier"
            and effect.get("multiplier") == 0.5 and effect.get("requiredAttackAbility") == "strength"
            and timed_row.get("repeatSaveAbility") == "constitution"
            and timed_row.get("repeatSaveDc") == source_save_dc
            and timed_row.get("repeatSaveTiming") == "target_turn_end"
            and browser_grants[0].get("resource_id") == "ray-of-enfeeblement"
            and browser.get("resources", {}).get("ray-of-enfeeblement") == int(source_uses)
        ):
            browser_wired.append(card.id)
        else:
            exceptions.append({"monster": card.id, "reason": "browser serialization lost Ray of Enfeeblement semantics"})
    return {
        "source_cards_scanned": len(cards), "applicable_card_count": len(applicable),
        "applicable_cards": applicable, "wired_python_card_count": len(python_wired),
        "wired_browser_card_count": len(browser_wired),
        "wired_cards": sorted(set(python_wired) & set(browser_wired)),
        "remaining_card_count": len(exceptions), "exceptions": exceptions,
        "source_cards_2024_audited": len(cards_2024),
        "applicable_2024_card_count": len(applicable_2024),
        "applicable_2024_cards": applicable_2024,
        "edition_audit_note": (
            "No 2024 source card declares the same Strength-weapon damage-halving debuff."
            if not applicable_2024 else
            "2024 semantic matches require independent source binding before certification."
        ),
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
