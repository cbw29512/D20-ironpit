from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ROOT / "data" / "simple_combat_spell_roster_v1.json"
EXPECTED_LEVELS = {
    "bard": range(1, 10),
    "cleric": range(1, 10),
    "druid": range(1, 10),
    "paladin": range(1, 6),
    "ranger": range(1, 6),
    "sorcerer": range(1, 10),
    "warlock": range(1, 10),
    "wizard": range(1, 10),
}


def _payload() -> dict[str, object]:
    return json.loads(ROSTER.read_text(encoding="utf-8"))


def test_every_caster_has_exactly_one_spell_per_available_spell_level() -> None:
    classes = _payload()["classes"]
    assert set(classes) == set(EXPECTED_LEVELS)
    for class_id, levels in EXPECTED_LEVELS.items():
        spells = classes[class_id]
        assert set(spells) == {str(level) for level in levels}
        assert len(spells.values()) == len(set(spells.values()))


def test_reuse_is_preferred_across_arcane_casters() -> None:
    classes = _payload()["classes"]
    assert classes["wizard"] == classes["sorcerer"]
    assert classes["wizard"]["1"] == "magic-missile"
    assert classes["wizard"]["3"] == "fireball"
    assert classes["wizard"]["4"] == "blight"


def test_complex_spells_are_explicitly_deferred() -> None:
    deferred = set(_payload()["defer_complex_examples"])
    assert {"animate-objects", "simulacrum", "true-polymorph", "wish"} <= deferred
