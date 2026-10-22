"""Compile a user-created monster through the canonical Iron Pit combat compiler.

Usage: python -m scripts.compile_custom_monster_card source.json destination.json
The output is a browser runtime template, not a claim of gameplay certification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Mapping

from app.content.combatant_form import compile_combatant_form
from scripts.browser_template_serializer import template_row


def compile_custom_monster(payload: Mapping[str, object]) -> dict:
    """Strictly accept declarative monster cards and export canonical browser rows."""
    if not isinstance(payload, Mapping):
        raise ValueError("A custom monster must be a JSON object.")
    if payload.get("kind") != "monster":
        raise ValueError("Only homebrew monsters can use this compiler; pregen RAW progression is required.")
    if payload.get("ruleset") not in ("2014", "2024"):
        raise ValueError("Custom monster requires a supported explicit ruleset.")
    if "custom" in payload or "coverage_status" in payload or "runnable_template_id" in payload:
        raise ValueError("Remove browser library metadata before compiling the source form.")
    template = compile_combatant_form(payload)
    if template.kind != "monster":
        raise ValueError("Compiled custom card must remain a monster.")
    return template_row(template)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Canonical custom monster JSON source")
    parser.add_argument("destination", type=Path, help="Browser template JSON output")
    args = parser.parse_args()
    data = json.loads(args.source.read_text(encoding="utf-8"))
    output = compile_custom_monster(data)
    args.destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
