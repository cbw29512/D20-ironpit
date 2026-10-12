"""2014 Grimlock: source-proven bounded Blindsight and loss-of-smell semantics."""
from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.conditions import attack_roll_condition_sources
from app.combat.effective_senses import effective_sense_range_ft, source_sense_range_ft
from app.combat.state import build_combatant_state
from app.combat.visibility_rules import can_see
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_senses_2014 import bounded_blindsight_2014, special_senses_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "grimlock")
    except Exception:
        logger.exception("2014 Grimlock pinned source is unavailable.")
        raise


def test_source_proof_is_immutable_and_whole_monster_admitted() -> None:
    source = _source()
    before = source.model_dump_json()
    assert "blinded" in source.condition_immunities
    assert bounded_blindsight_2014(source) == (30, 10)
    assert special_senses_2014(source) == (30, 0)
    assert basic_blockers_2014(source) == ()
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.blindsight_ft == 30
    assert template.blindsight_deafened_ft == 10
    assert template.blind_beyond_blindsight
    assert template.blindsight_requires_smell_when_deafened
    wire = template_row(template)
    assert wire["blindsight_ft"] == 30
    assert wire["blindsight_deafened_ft"] == 10
    assert wire["blind_beyond_blindsight"]
    assert wire["blindsight_requires_smell_when_deafened"]
    assert template.source_trait_names == source.trait_names
    assert source.model_dump_json() == before


def test_bounded_range_deafness_and_smell_are_shared_live_fight_state() -> None:
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    observer = build_combatant_state(template)
    defender = build_combatant_state(build_demo_fighter())
    assert not has_condition(observer, "blinded")
    assert source_sense_range_ft(observer, "blindsight") == 30
    assert effective_sense_range_ft(observer, "blindsight") == 30
    assert can_see(observer, defender, 30)
    assert not can_see(observer, defender, 35)
    _, nearby = attack_roll_condition_sources(observer, defender, 30)
    _, remote = attack_roll_condition_sources(observer, defender, 35)
    assert remote == nearby + 1

    observer.active_effect_ids.append("deafened")
    assert effective_sense_range_ft(observer, "blindsight") == 10
    assert can_see(observer, defender, 10)
    assert not can_see(observer, defender, 15)
    observer.suppressed_sense_ids.append("smell")
    assert effective_sense_range_ft(observer, "blindsight") == 0
    assert not can_see(observer, defender, 5)
    observer.active_effect_ids.remove("deafened")
    assert effective_sense_range_ft(observer, "blindsight") == 30
    observer.suppressed_sense_ids.clear()
    assert can_see(observer, defender, 30)

    fresh = build_combatant_state(template)
    assert fresh.suppressed_sense_ids == []
    assert fresh.active_effect_ids == []
    assert effective_sense_range_ft(fresh, "blindsight") == 30


def test_blind_senses_drift_fails_closed_without_adding_runnable_trait() -> None:
    source = _source()
    wrong_range = source.model_copy(update={
        "senses": source.senses.replace("while deafened", "while frightened"),
    })
    assert wrong_range.senses != source.senses
    assert bounded_blindsight_2014(wrong_range) is None
    assert "source:trait" in basic_blockers_2014(wrong_range)
    altered_trait = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace("unable to smell", "unable to hear"),
    })
    assert altered_trait.source_traits != source.source_traits
    assert bounded_blindsight_2014(altered_trait) is None
    assert "source:trait" in basic_blockers_2014(altered_trait)
