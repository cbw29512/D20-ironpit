"""Card-declared illusion death expiry across generic lethal paths."""
from __future__ import annotations

import pytest
from app.combat.visual_disguise_death_lifecycle import end_visual_disguise_if_dead
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.zero_hp import _mark_dead
from app.combat.instant_death import apply_terminal_death
from app.combat.exhaustion import gain_exhaustion
from app.combat.state import build_combatant_state
from app.domain.visual_disguise import VisualDisguiseAction
from test_2014_visual_disguise_opening import _setup


def _masked():
    setup, member, observer = _setup()
    prepare_opening_buffs(setup)
    assert member.state.magical_visual_disguise_active
    return member, observer


@pytest.mark.parametrize("method", ["ordinary-zero-hp", "terminal-death", "exhaustion"])
def test_source_declared_visual_disguise_ends_only_on_actual_death(method):
    source, observer = _masked()
    printed = source.state.template.visual_disguise_action
    original = printed.model_dump_json()
    if method == "ordinary-zero-hp":
        assert _mark_dead(source.state) == "dead"
    elif method == "terminal-death":
        assert apply_terminal_death(source.state) == "dead"
    else:
        assert gain_exhaustion(source.state, 6) == 6
    assert source.state.is_dead
    assert not source.state.magical_visual_disguise_active
    assert original == printed.model_dump_json()
    assert build_combatant_state(source.state.template).magical_visual_disguise_active is False
    assert end_visual_disguise_if_dead(source.state) is False


def test_unconscious_or_not_yet_dead_does_not_expire_disguise():
    source, observer = _masked()
    source.state.is_unconscious = True
    assert not end_visual_disguise_if_dead(source.state)
    assert source.state.magical_visual_disguise_active
    source.state.is_unconscious = False
    source.state.current_hp = 1
    assert not end_visual_disguise_if_dead(source.state)


def test_other_source_card_can_declare_disguise_persists_on_death():
    source, observer = _masked()
    printed = source.state.template.visual_disguise_action
    overridden = VisualDisguiseAction.model_validate(
        printed.model_dump() | {"name": "Renamed Pregen", "ends_if_owner_dead": False}
    )
    source.state.template = source.state.template.model_copy(update={
        "kind": "character", "visual_disguise_action": overridden,
    })
    source.state.is_dead = True
    assert not end_visual_disguise_if_dead(source.state)
    assert source.state.magical_visual_disguise_active
