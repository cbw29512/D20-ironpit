"""2014 Sea Hag full source-admission proof after universal visual-disguise support."""
from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014,
    is_basic_candidate_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_conditioned_save_2014 import source_proven_conditioned_saves_2014
from app.content.monster_visual_disguise_2014 import visual_disguise_action_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014


def _hag():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "sea-hag")
    except Exception as exc:
        raise AssertionError("Missing pinned 2014 Sea Hag") from exc


def test_complete_source_is_admitted_only_through_bound_universal_capabilities():
    try:
        source = _hag()
        snapshot = source.model_dump_json()
        disguise = visual_disguise_action_2014(source)
        gaze = visual_turn_start_rule_2014(source)
        death_glare = source_proven_conditioned_saves_2014(source)

        assert disguise is not None and disguise.physical_inspection_inconsistent
        assert disguise.ends_if_owner_dead and disguise.inspection_dc == 16
        assert gaze is not None and gaze.source_name == "Horrific Appearance"
        assert [action.name for action in death_glare] == ["Death Glare"]
        assert basic_blockers_2014(source) == ()
        assert is_basic_candidate_2014(source)

        template = compile_combatant(adapt_basic_monster_2014(source))
        assert template.visual_disguise_action == disguise
        assert template.visual_turn_start_rule == gaze
        assert any(action.name == "Death Glare" for action in template.saving_throw_actions)
        assert source.model_dump_json() == snapshot
    except Exception:
        raise


def test_monster_identity_is_not_an_admission_dispatch_key():
    try:
        source = _hag()
        renamed = source.model_copy(update={
            "id": "renamed-visual-controller",
            "name": "Unrelated Visual Controller",
        })
        assert visual_disguise_action_2014(renamed) is not None
        assert visual_turn_start_rule_2014(renamed) is not None
        assert source_proven_conditioned_saves_2014(renamed)
        assert basic_blockers_2014(renamed) == ()
    except Exception:
        raise


def test_changed_tactile_clause_fails_closed_and_restores_extra_action_blocker():
    try:
        source = _hag()
        changed = source.model_copy(update={
            "source_actions": source.source_actions.replace(
                "fail to hold up to physical inspection",
                "always hold up to physical inspection",
            ),
        })
        assert visual_disguise_action_2014(changed) is None
        assert "source:extra-action" in basic_blockers_2014(changed)
    except Exception:
        raise


def test_changed_horrific_appearance_fails_closed_and_restores_trait_blocker():
    try:
        source = _hag()
        changed = source.model_copy(update={
            "source_traits": source.source_traits.replace(
                "frightened for 1 minute", "frightened for 2 minutes",
            ),
        })
        assert visual_turn_start_rule_2014(changed) is None
        assert "source:trait" in basic_blockers_2014(changed)
    except Exception:
        raise
