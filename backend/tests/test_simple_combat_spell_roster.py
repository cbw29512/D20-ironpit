from __future__ import annotations

import json
from pathlib import Path

from app.content.class_spell_progression import prepared_spell_count

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ROOT / "data" / "simple_combat_spell_roster_v1.json"
CASTERS = ("bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard")


def _payload() -> dict[str, object]:
    return json.loads(ROSTER.read_text(encoding="utf-8"))


def test_every_caster_has_enough_unique_level20_combat_spells() -> None:
    payload = _payload()
    classes = payload["classes"]
    required = payload["level20_required_prepared_counts"]
    assert set(classes) == set(CASTERS)
    for class_id in CASTERS:
        spells = classes[class_id]
        assert len(spells) == len(set(spells))
        assert len(spells) >= prepared_spell_count(class_id, 20)
        assert required[class_id] == prepared_spell_count(class_id, 20)


def test_easy_first_set_targets_only_reusable_spell_primitives() -> None:
    payload = _payload()
    primitives = set(payload["preferred_primitives"])
    assert {"auto-hit-damage", "save-half-damage", "spell-attack", "healing"} <= primitives
    easy = set(payload["easy_first"])
    assert {"magic-missile", "fireball", "cone-of-cold", "ice-storm", "heal"} <= easy


def test_complex_spells_are_explicitly_deferred() -> None:
    payload = _payload()
    deferred = set(payload["defer_complex_examples"])
    assert {"animate-objects", "simulacrum", "true-polymorph", "wish"} <= deferred
