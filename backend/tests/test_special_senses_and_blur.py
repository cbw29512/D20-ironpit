from __future__ import annotations

from app.combat.defensive_modifier_rules import attacks_against_disadvantage_sources
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_2024_spells import build_blur_2024
from app.content.monster_catalog import load_monster_rows
from app.content.monster_special_senses import parse_special_senses


def test_special_sense_parser_reads_source_blindsight_and_truesight_ranges() -> None:
    crab = next(row for row in load_monster_rows() if row["name"] == "Crab")
    assert parse_special_senses(crab) == (30, 0)

    synthetic = {
        "name": "Test Seer",
        "rawText": "Senses Blindsight 10 ft., Truesight 60 ft.; Passive Perception 14 Languages Common CR 1",
    }
    assert parse_special_senses(synthetic) == (10, 60)


def _blurred_state():
    defender = build_thalen_greenbough_level(2)
    state = build_combatant_state(defender)
    blur = build_blur_2024()
    modifier = build_spell_modifier(
        "druid",
        "druid",
        blur.id,
        blur.modifier_effects[0],
        0,
        blur.name,
        concentration_required=True,
        round_number=1,
    )
    state.active_modifiers.append(modifier)
    return state, defender


def test_blur_disadvantage_is_bypassed_only_inside_declared_special_sense_range() -> None:
    state, base = _blurred_state()
    normal = base.model_copy(update={"id": "normal-attacker", "blindsight_ft": 0, "truesight_ft": 0})
    blind = base.model_copy(update={"id": "blind-attacker", "blindsight_ft": 10, "truesight_ft": 0})
    true = base.model_copy(update={"id": "true-attacker", "blindsight_ft": 0, "truesight_ft": 60})

    assert attacks_against_disadvantage_sources(state, normal, 5) == 1
    assert attacks_against_disadvantage_sources(state, blind, 5) == 0
    assert attacks_against_disadvantage_sources(state, blind, 10) == 0
    assert attacks_against_disadvantage_sources(state, blind, 15) == 1
    assert attacks_against_disadvantage_sources(state, true, 60) == 0
    assert attacks_against_disadvantage_sources(state, true, 65) == 1
