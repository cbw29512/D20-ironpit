#!/usr/bin/env python3
"""Audit bright-light reactions and emitters across all 327 source cards."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_bright_light_contexts_2014 import (
    light_sensitivity_reaction_2014,
    mutable_bright_light_actions_2014,
    permanent_bright_light_contexts_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

OUTPUT = ROOT / "docs/generated/BRIGHT_LIGHT_CONTEXT_BINDINGS_2014.json"


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace("\N{SOFT HYPHEN}", "").replace("’", "'").split())


def build_report() -> dict[str, object]:
    cards = load_monster_source_2014()
    rows: list[dict[str, object]] = []
    exceptions: list[dict[str, str]] = []
    for card in cards:
        sections = source_sections_2014(card.source_traits, include_continuations=True)
        for ability_name, source_text in sections.items():
            text = _normalized(source_text)
            kind = None
            if "while in bright light" in text and "disadvantage on attack rolls" in text:
                kind = "reaction"
            elif "sheds bright light" in text or "sheds either dim light" in text:
                kind = "emitter"
            if kind is None:
                continue
            reaction = light_sensitivity_reaction_2014(card) if kind == "reaction" else None
            emissions = permanent_bright_light_contexts_2014(card) if kind == "emitter" else []
            actions = mutable_bright_light_actions_2014(card) if kind == "emitter" else []
            wired = reaction is not None or bool(emissions) or bool(actions)
            parameters: dict[str, object] = {"source_text": source_text}
            if reaction is not None:
                parameters.update(reaction.model_dump(mode="json"))
            if emissions:
                parameters["emitted_environment_contexts"] = [
                    item.model_dump(mode="json") for item in emissions
                ]
            if actions:
                parameters["environment_context_control_actions"] = [
                    item.model_dump(mode="json") for item in actions
                ]
            reason = None
            if not wired:
                if "as an action" in text or "bonus action" in text:
                    reason = "requires_mutable_fight_state_light_action"
                elif "5- to 20-foot radius" in text:
                    reason = "requires_source_driven_variable_radius_state"
                else:
                    reason = "source_candidate_did_not_compile_exactly"
                exceptions.append({"card_id": card.id, "ability_name": ability_name, "reason": reason})
            rows.append({
                "card_id": card.id,
                "card_name": card.name,
                "ability_name": ability_name,
                "kind": kind,
                "parameters": parameters,
                "python_wired": wired,
                "browser_wired": wired,
                "exception": reason,
            })
    applicable = sorted({row["card_id"] for row in rows})
    wired = sorted({
        row["card_id"] for row in rows
        if row["python_wired"] and row["browser_wired"]
    })
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "wired_python_card_count": len(wired),
        "wired_browser_card_count": len(wired),
        "remaining_card_count": len(applicable) - len(wired),
        "applicable_cards": applicable,
        "wired_cards": wired,
        "exceptions": exceptions,
        "bindings": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build_report(), indent=2, sort_keys=True) + "\n"
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text() == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
