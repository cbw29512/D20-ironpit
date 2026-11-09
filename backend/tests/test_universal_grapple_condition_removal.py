"""Universal condition removal must release Grapple-owned conditions together."""
from __future__ import annotations

from app.combat.condition_removal import remove_condition
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.state import build_combatant_state
from app.combat.timed_condition_apply import apply_timed_condition
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant


def _target(label: str):
    template = build_demo_fighter().model_copy(update={"name": label})
    return EncounterCombatant(
        combatant_id=label, side="heroes", position_ft=0,
        state=build_combatant_state(template),
    )


def test_removing_grappled_cleans_source_owned_restrained_and_blindness():
    target = _target("Held Fighter")
    apply_grapple(
        target.state, "source-crocodile", 12, 5,
        restrains=True, blinds=True, prevents_breathing=True,
    )
    assert {"grappled", "restrained", "blinded"} <= set(target.state.active_effect_ids)
    remove_condition(target, "grappled")
    assert not target.state.grapple_sources
    assert not {"grappled", "restrained", "blinded"} & set(target.state.active_effect_ids)


def test_grapple_release_preserves_independent_timed_restrained_condition():
    target = _target("Other Restrained Fighter")
    assert apply_timed_condition(
        target.state, "restrained", "different-spell",
        expires_at_start_of_source_turn=False, expiry_timing=None,
    ) == "restrained"
    apply_grapple(target.state, "source-crocodile", 12, 5, restrains=True)
    remove_condition(target, "grappled")
    assert not target.state.grapple_sources
    assert "grappled" not in target.state.active_effect_ids
    assert "restrained" in target.state.active_effect_ids
    assert any(
        effect.effect_id == "restrained" and effect.source_id == "different-spell"
        for effect in target.state.timed_effects
    )


def test_releasing_one_source_preserves_another_grapple_then_removes_all():
    target = _target("Two Sources")
    apply_grapple(target.state, "source-a", 12, 5, restrains=True)
    apply_grapple(target.state, "source-b", 13, 5, restrains=False)
    release_grapple(target.state, "source-a")
    assert {src.source_id for src in target.state.grapple_sources} == {"source-b"}
    assert "grappled" in target.state.active_effect_ids
    assert "restrained" not in target.state.active_effect_ids
    remove_condition(target, "grappled")
    assert not target.state.grapple_sources
    assert "grappled" not in target.state.active_effect_ids
