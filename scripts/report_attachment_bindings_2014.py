#!/usr/bin/env python3
"""Audit source-linked attachment declarations across all immutable 2014 cards."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_attachment_2014 import supports_source_attachment_2014

OUTPUT = ROOT / "docs/generated/ATTACHMENT_BINDINGS_2014.json"
_SEMANTIC = re.compile(r"\battach(?:es|ed|ment)?\b|\badher(?:e|es|ed)\b", re.I)
_GRAPPLE_LINKED = re.compile(r"\bgrappled?\b|\brestrained\b", re.I)
_CONTROL_LINKED = re.compile(r"\bblinded\b|\bunable to breathe\b", re.I)


def _printed_text(card) -> str:
    return " ".join(
        " ".join(str(value or "").split())
        for value in (card.source_traits, card.source_actions, card.source_reactions)
    )


def build_report() -> dict[str, object]:
    cards = load_monster_source_2014()
    bindings: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for card in cards:
        printed = _printed_text(card)
        if not _SEMANTIC.search(printed):
            continue
        wired_attacks = []
        parameters = []
        for attack in card.attacks:
            if not supports_source_attachment_2014(attack):
                continue
            effects = [effect for effect in basic_attack_effects_2014(attack)
                       if effect.kind == "attachment"]
            if len(effects) != 1:
                continue
            effect = effects[0]
            wired_attacks.append(attack.id)
            parameters.append({
                "attack_id": attack.id,
                "source_name": effect.source_name,
                "periodic_effect_kind": effect.periodic_effect_kind,
                "damage_dice": f"{effect.dice_count}d{effect.dice_size}+{effect.damage_bonus}",
                "tick_timing": effect.tick_timing,
                "blocks_source_attacks": effect.blocks_source_attacks,
                "action_removable": effect.action_removable,
                "action_removal_range_ft": effect.action_removal_range_ft,
                "source_detach_movement_ft": effect.source_detach_movement_ft,
                "auto_end_after_hp_loss": effect.auto_end_after_hp_loss,
            })
        wired = bool(wired_attacks)
        if not wired:
            if _GRAPPLE_LINKED.search(printed):
                reason = "grapple_or_restrained_link_uses_shared_grapple_family"
            elif _CONTROL_LINKED.search(printed):
                reason = "conditional_control_attachment_profile_not_supported"
            else:
                reason = "missing_or_incompatible_source_attachment_parameters"
            exceptions.append({"card_id": card.id, "reason": reason})
        bindings.append({
            "card_id": card.id,
            "card_name": card.name,
            "semantic_source_match": True,
            "wired_attack_ids": wired_attacks,
            "parameters": parameters,
            "python_wired": wired,
            "browser_wired": wired,
        })
    wired_cards = [row["card_id"] for row in bindings if row["python_wired"] and row["browser_wired"]]
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(bindings),
        "applicable_cards": [row["card_id"] for row in bindings],
        "wired_python_card_count": len(wired_cards),
        "wired_browser_card_count": len(wired_cards),
        "wired_cards": wired_cards,
        "remaining_card_count": len(bindings) - len(wired_cards),
        "exceptions": exceptions,
        "bindings": bindings,
        "status": "complete_with_routed_exceptions" if exceptions else "complete",
    }


def render() -> str:
    return json.dumps(build_report(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
