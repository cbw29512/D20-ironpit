"""Single-pass 327-monster Multiattack coverage, reusing existing compiler.

Usage: python scripts/report_monster_multiattack_2014.py
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from app.content.monster_multiattack_2014 import multiattack_blockers_2014
from app.content.monster_multiattack_variants_2014 import (
    source_form_qualified_multiattack_labels_2014,
    source_multiattack_text_2014,
)
from app.content.monster_save_source_audit_2014 import unsupported_source_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from browser_template_serializer import template_row

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/generated/MULTIATTACK_SLOT_POLICY_BINDINGS_2014.json"


def report() -> dict[str, object]:
    monsters = load_monster_source_2014()
    counts: Counter[str] = Counter()
    missing: list[dict[str, object]] = []
    policy_family: list[dict[str, object]] = []
    qualified_heading_family: list[dict[str, object]] = []
    for card in monsters:
        # Source cards without Multiattack have no sequence to bind.
        printed = source_multiattack_text_2014(card) or None
        declared = bool(
            card.multiattack_slots or card.multiattack_binding is not None
            or card.multiattack_policy is not None
        )
        if printed is None and not declared:
            counts["not_applicable"] += 1
            continue
        reasons = (
            ["multiattack:source-unbound"] if printed and not declared
            else ["multiattack:missing-source"] if not printed
            else multiattack_blockers_2014(card)
        )
        if reasons:
            counts["blocked"] += 1
            missing.append({
                "monster": card.id,
                "reasons": reasons,
                "printed_multiattack": printed,
                "source_slots": card.multiattack_slots,
                "source_policy": card.multiattack_policy,
                "source_binding": card.multiattack_binding,
            })
        else:
            counts["bound"] += 1
        qualified_labels = source_form_qualified_multiattack_labels_2014(card)
        if qualified_labels:
            runtime = None
            browser_action: dict[str, object] = {}
            if not reasons:
                runtime = compile_combatant(adapt_monster_mechanics_2014(card))
                browser_action = template_row(runtime).get("attack_action", {})
            unresolved_actions = {
                action.casefold() for action in unsupported_source_actions_2014(card)
            }
            source_classified = qualified_labels.isdisjoint(unresolved_actions)
            python_wired = bool(runtime and runtime.attack_action)
            browser_wired = bool(browser_action.get("slots") or browser_action.get("variants"))
            qualified_heading_family.append({
                "monster": card.id,
                "labels": sorted(qualified_labels),
                "source_classified": source_classified,
                "python_wired": python_wired,
                "browser_wired": browser_wired,
                "wired": source_classified and python_wired and browser_wired,
                "reasons": reasons + ([] if source_classified else ["source:extra-action"]),
            })
        if isinstance(card.multiattack_policy, dict) and (
            "at_most_once_attack_ids" in card.multiattack_policy
            or "same_attack_as_previous_slots" in card.multiattack_policy
        ):
            python_wired = not reasons
            browser_wired = False
            if python_wired:
                runtime = compile_combatant(adapt_monster_mechanics_2014(card))
                python_variants = runtime.attack_action.variants if runtime.attack_action else []
                browser_action = template_row(runtime).get("attack_action", {})
                browser_variants = browser_action.get("variants", [])
                browser_wired = len(browser_variants) == len(python_variants) > 0 and all(
                    browser["attackKind"] == (
                        variant.attack_kind.value if variant.attack_kind else None
                    )
                    and browser["slots"] == [
                        {
                            "attackIds": slot.attack_ids,
                            "saveActionIds": slot.save_action_ids,
                        }
                        for slot in variant.slots
                    ]
                    for browser, variant in zip(browser_variants, python_variants)
                )
            policy_family.append({
                "monster": card.id,
                "python_wired": python_wired,
                "browser_wired": browser_wired,
                "wired": python_wired and browser_wired,
                "reasons": reasons,
                "source_policy": card.multiattack_policy,
            })
    if len(monsters) != 327:
        raise ValueError("Expected 327 distinct 2014 monster cards")
    family_remaining = [item for item in policy_family if not item["wired"]]
    heading_remaining = [item for item in qualified_heading_family if not item["wired"]]
    return {
        "source_monsters": 327,
        "counts": dict(sorted(counts.items())),
        "policy_family": {
            "applicable": len(policy_family),
            "wired_python": sum(bool(item["python_wired"]) for item in policy_family),
            "wired_browser": sum(bool(item["browser_wired"]) for item in policy_family),
            "wired": len(policy_family) - len(family_remaining),
            "remaining": len(family_remaining),
            "exceptions": family_remaining,
            "cards": policy_family,
        },
        "form_qualified_heading_family": {
            "applicable": len(qualified_heading_family),
            "source_classified": sum(
                bool(item["source_classified"]) for item in qualified_heading_family
            ),
            "wired_python": sum(bool(item["python_wired"]) for item in qualified_heading_family),
            "wired_browser": sum(bool(item["browser_wired"]) for item in qualified_heading_family),
            "wired": len(qualified_heading_family) - len(heading_remaining),
            "remaining": len(heading_remaining),
            "exceptions": heading_remaining,
            "cards": qualified_heading_family,
        },
        "unresolved": missing,
    }


def render() -> str:
    return json.dumps(report(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        return 0 if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered else 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
