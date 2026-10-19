"""Schema contract for source-owned visual effects; no monster dispatch."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.turn_start_visual_policy import VisualTurnStartRule
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014


@pytest.mark.parametrize("monster_id,dc,margin", [
    ("basilisk", 12, None),
    ("medusa", 14, 5),
])
def test_source_rule_round_trip(monster_id: str, dc: int, margin: int | None) -> None:
    source = next(m for m in load_monster_source_2014() if m.id == monster_id)
    before = source.model_dump_json()
    rule = visual_turn_start_rule_2014(source)
    assert rule is not None
    assert rule.save_dc == dc
    assert rule.immediate_petrification_margin == margin
    assert rule.range_ft == 30
    assert VisualTurnStartRule.model_validate(rule.model_dump()) == rule
    assert source.model_dump_json() == before


@pytest.mark.parametrize("change", [
    {"range_ft": True},
    {"save_dc": False},
    {"save_dc": 41},
    {"source_name": " "},
    {"initial_debuff": "petrified"},
    {"immediate_petrification_margin": 0},
])
def test_source_rule_rejects_corrupt_parameters(change: dict[str, object]) -> None:
    valid = {"source_id": "source", "source_name": "Source", "range_ft": 30, "save_dc": 12}
    with pytest.raises(ValidationError):
        VisualTurnStartRule(**(valid | change))
