"""Immutable card-definition binding for source-owned visual turn-start parameters."""
from __future__ import annotations

import pytest

from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014
from app.domain.capabilities import CombatantDefinition


@pytest.mark.parametrize("monster_id,dc,margin", [
    ("basilisk", 12, None),
    ("medusa", 14, 5),
])
def test_visual_rule_round_trips_through_immutable_card_definition(
    monster_id: str, dc: int, margin: int | None,
) -> None:
    source = {monster.id: monster for monster in load_monster_source_2014()}
    rule = visual_turn_start_rule_2014(source[monster_id])
    assert rule is not None
    assert rule.save_dc == dc
    assert rule.immediate_petrification_margin == margin

    # Use an already-admitted monster only to exercise the generic card schema.
    # This does not bypass the two gaze monsters' runtime certification gate.
    definition = adapt_basic_monster_2014(source["giant-rat"])
    with_rule = definition.model_copy(update={"visual_turn_start_rule": rule})
    restored = CombatantDefinition.model_validate(with_rule.model_dump())
    assert restored.visual_turn_start_rule == rule
    assert restored.visual_turn_start_rule is not rule
    assert definition.visual_turn_start_rule is None


def test_visual_failure_margin_requires_printed_instant_petrification() -> None:
    source = {m.id: m for m in load_monster_source_2014()}
    medusa = source["medusa"]
    assert visual_turn_start_rule_2014(medusa) is not None
    altered = medusa.model_copy(update={
        "source_traits": medusa.source_traits.replace(
            "instantly petrified", "instead remains restrained"
        )
    })
    assert altered.source_traits != medusa.source_traits
    assert visual_turn_start_rule_2014(altered) is None


@pytest.mark.parametrize("monster_id", ["basilisk", "medusa"])
def test_source_proven_gaze_monster_is_admitted_and_compiles(monster_id: str) -> None:
    monster = next(row for row in load_monster_source_2014() if row.id == monster_id)
    assert basic_blockers_2014(monster) == ()
    definition = adapt_basic_monster_2014(monster)
    assert definition.visual_turn_start_rule is not None
    assert definition.visual_turn_start_rule.source_name == "Petrifying Gaze"
