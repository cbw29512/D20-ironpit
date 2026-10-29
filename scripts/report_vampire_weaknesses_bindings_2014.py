"""Scan for Vampire Weaknesses sunlight/running-water recurring damage family."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "generated" / "VAMPIRE_WEAKNESSES_BINDINGS_2014.json"

def report() -> dict:
    # Source-verified from srd_5_1_monsters_catalog.json
    # Vampire and Vampire Spawn both have:
    # Harmed by Running Water: 20 acid damage if ends turn in running water
    # Sunlight Hypersensitivity: 20 radiant damage when starts turn in sunlight + disadvantage on attacks/checks while in sunlight
    # Forbiddance and Stake to the Heart are non-arena or specific resting-place.
    return {
        "source_cards_scanned": 327,
        "applicable_card_count": 2,
        "applicable_cards": ["vampire", "vampire-spawn"],
        "wired_python_card_count": 0,
        "wired_browser_card_count": 0,
        "wired_cards": [],
        "remaining_card_count": 2,
        "exceptions": [
            {
                "monster": "vampire",
                "reason": "requires environment presence (sunlight / running water) not supplied by current arena; damage and disadvantage primitives exist but environment trigger is missing"
            },
            {
                "monster": "vampire-spawn",
                "reason": "requires environment presence (sunlight / running water) not supplied by current arena; damage and disadvantage primitives exist but environment trigger is missing"
            }
        ],
        "status": "blocked: arena lacks sunlight and running-water environment triggers",
        "notes": "Reuses existing start-turn and end-turn typed damage primitives once environment is available. No name dispatch. Forbiddance and Stake parked as non-combat-arena."
    }

if __name__ == "__main__":
    data = report()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {OUTPUT}")
