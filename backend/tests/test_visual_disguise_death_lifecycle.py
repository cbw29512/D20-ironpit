from __future__ import annotations

from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.state import build_combatant_state
from test_2014_visual_disguise_opening import _setup


def _renamed_disguise(*, ends_if_owner_dead: bool):
    setup, source, observer = _setup()
    declared = source.state.template.visual_disguise_action
    renamed = declared.model_copy(update={
        "name": "Unrelated Visual Mask",
        "ends_if_owner_dead": ends_if_owner_dead,
    })
    source.state.template = source.state.template.model_copy(update={
        "name": "Renamed Source",
        "visual_disguise_action": renamed,
    })
    source.state = build_combatant_state(source.state.template)
    prepare_opening_buffs(setup)
    assert source.state.magical_visual_disguise_active
    return setup, source, observer, renamed


def test_declared_visual_disguise_expires_when_owner_dies() -> None:
    setup, source, _observer, declared = _renamed_disguise(
        ends_if_owner_dead=True,
    )

    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    cleanup_disabled_source_effects(setup)

    assert source.state.magical_visual_disguise_active is False
    assert source.state.template.visual_disguise_action == declared
    assert build_combatant_state(
        source.state.template,
    ).magical_visual_disguise_active is False


def test_visual_disguise_without_owner_death_exit_is_not_invented() -> None:
    setup, source, _observer, declared = _renamed_disguise(
        ends_if_owner_dead=False,
    )

    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    cleanup_disabled_source_effects(setup)

    assert source.state.magical_visual_disguise_active is True
    assert source.state.template.visual_disguise_action == declared
