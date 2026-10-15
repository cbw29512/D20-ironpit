from __future__ import annotations

import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014


@pytest.mark.parametrize("monster_id,dc,margin", [
    ("basilisk", 12, None),
    ("medusa", 14, 5),
])
def test_pinned_2014_gaze_source_parameters(monster_id, dc, margin):
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    original = monster.model_dump_json()
    rule = visual_turn_start_rule_2014(monster)
    assert rule is not None
    assert rule.source_name == "Petrifying Gaze"
    assert rule.range_ft == 30
    assert rule.save_ability == "constitution"
    assert rule.save_dc == dc
    assert rule.immediate_petrification_margin == margin
    assert monster.model_dump_json() == original


@pytest.mark.parametrize("monster_id", ["basilisk", "medusa"])
def test_source_tampering_cannot_silently_enable_visual_rule(monster_id):
    monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
    altered = monster.model_copy(update={
        "source_traits": (monster.source_traits or "").replace(
            "within 30 feet", "at any distance"
        ),
    })
    assert visual_turn_start_rule_2014(altered) is None
