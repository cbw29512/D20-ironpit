"""Create a deterministic cross-runtime fixture from the real homebrew form compiler."""
from __future__ import annotations

import json
from pathlib import Path

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.combatant_form import compile_combatant_form
from scripts.browser_template_serializer import template_row

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "frontend" / "browser-form-runtime-parity-fixture.json"


def form(kind: str) -> dict:
    payload = {
        "schema_version": 1, "id": "fixture-attacker", "name": "Fixture",
        "archetype": "custom", "kind": kind, "ruleset": "2014",
        "armor_class": 14, "max_hp": 31, "speed_ft": 30, "initiative_bonus": 2,
        "attacks": [{
            "id": "fixture-attack", "name": "Arbitrary Attack",
            "attack_kind": "melee", "attack_bonus": 5,
            "damage": {"count": 2, "size": 6, "bonus": 2},
            "damage_type": "bludgeoning", "animation": "slash",
        }],
        "primary_attack_id": "fixture-attack",
        "source": "synthetic cross-runtime parity fixture",
        "visual": {"armor": "natural", "main_hand": "claw", "body_style": "beast"},
    }
    if kind == "character":
        payload.update(level=1, ability_scores={
            "strength": 16, "dexterity": 14, "constitution": 16,
            "intelligence": 10, "wisdom": 12, "charisma": 10,
        })
    return payload


def main() -> None:
    defender_form = form("monster")
    defender_form.update(id="fixture-target", armor_class=10, max_hp=100)
    defender = compile_combatant_form(defender_form)
    cases = []
    for kind in ("monster", "character"):
        attacker = compile_combatant_form(form(kind))
        attacker_state = build_combatant_state(attacker)
        defender_state = build_combatant_state(defender)
        event = resolve_attack(
            1, 1, attacker_state, defender_state, attacker.weapon_attack, 5,
            FixedDiceProvider([15, 4, 5]), actor_event_id="attacker",
            target_event_id="target", spend_action=False,
        )
        cases.append({
            "kind": kind, "attacker": template_row(attacker),
            "defender": template_row(defender),
            "expected": {
                "hit": event.hit, "damage": event.damage_roll.total,
                "hp": defender_state.current_hp,
            },
        })
    DEST.write_text(json.dumps({"cases": cases}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
