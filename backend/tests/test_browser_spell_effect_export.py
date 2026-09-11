from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from app.content.spell_effects import BLESS, SHIELD_OF_FAITH  # noqa: E402
from browser_action_serializer import defense_row  # noqa: E402


def test_defensive_spell_serializer_uses_current_duration_and_modifier_schema() -> None:
    bless = defense_row(BLESS)
    shield = defense_row(SHIELD_OF_FAITH)

    assert bless["durationMinutes"] == 1
    assert bless["range"] == 30
    assert bless["targetPolicy"] == "friendly"
    assert bless["targetCount"] == 3
    assert [effect["kind"] for effect in bless["modifierEffects"]] == [
        "attack-roll-bonus-die",
        "saving-throw-bonus-die",
    ]
    assert "durationRounds" not in bless
    assert "temporaryAcBonus" not in bless

    assert shield["durationMinutes"] == 10
    assert shield["actionCost"] == "bonus_action"
    assert shield["modifierEffects"] == [
        {
            "kind": "armor-class",
            "flatBonus": 2,
            "diceCount": 0,
            "diceSize": 0,
            "damageType": None,
        }
    ]
