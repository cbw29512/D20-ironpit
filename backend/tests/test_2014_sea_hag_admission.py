"""Real 2014 Sea Hag admission through existing universal visual mechanics."""
from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_supported_extra_actions_2014 import source_supported_extra_action_labels_2014

logger = logging.getLogger(__name__)


def _hag():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "sea-hag")
    except StopIteration as exc:
        logger.exception("Pinned 2014 Sea Hag source missing")
        raise AssertionError("Missing canonical Sea Hag source") from exc


def test_sea_hag_admits_with_complete_existing_universal_capabilities():
    source = _hag()
    before = source.model_dump_json()
    assert basic_blockers_2014(source) == ()
    definition = adapt_basic_monster_2014(source)
    template = compile_combatant(definition)
    assert template.id == "2014-sea-hag"
    assert template.visual_disguise_action is not None
    assert template.visual_disguise_action.name == "Illusory Appearance"
    assert template.visual_disguise_action.inspection_dc == 16
    assert template.visual_turn_start_rule is not None
    assert template.visual_turn_start_rule.source_name == "Horrific Appearance"
    glare = next(a for a in template.saving_throw_actions if a.id == "death-glare")
    assert glare.name == "Death Glare" and glare.dc == 11
    assert glare.required_target_condition == "frightened"
    assert glare.failure_sets_zero_hp
    state = build_combatant_state(template)
    assert state.magical_visual_disguise_active is False
    assert source.model_dump_json() == before


def test_unproved_illusion_action_remains_an_extra_action_blocker():
    source = _hag()
    for original, mutated in (
        ("magical illusion", "ordinary costume"),
        ("DC 16 Intelligence (Investigation)", "DC 16 Wisdom (Perception)"),
        ("takes a bonus action to end it", "takes an action to end it"),
    ):
        assert original in source.source_actions
        changed = source.model_copy(update={
            "source_actions": source.source_actions.replace(original, mutated)
        })
        assert "illusory appearance" not in source_supported_extra_action_labels_2014(changed)
        assert "source:extra-action" in basic_blockers_2014(changed)
        assert basic_blockers_2014(source) == ()


def test_missing_illusion_heading_does_not_silently_admit_action():
    source = _hag()
    changed = source.model_copy(update={
        "source_actions": source.source_actions.replace(
            "<strong>Illusory Appearance.</strong>",
            "<strong>Unknown Illusion.</strong>",
        ),
    })
    assert "source:extra-action" in basic_blockers_2014(changed)
