from app.combat.action_economy import is_available, spend
from app.combat.encounter_setup import build_encounter_setup
from app.combat.save_failure_effects import apply_save_failure_effects
from app.combat.state import begin_turn
from app.domain.models import EncounterSelection
from app.domain.save_effects import TurnRestrictionEffectDefinition


def _state():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-goblin-warrior"],
    ))
    return setup.heroes[0].state


def _effect(*, requires_condition=None):
    return TurnRestrictionEffectDefinition(
        action_or_bonus_only=True,
        reactions_disabled=True,
        requires_condition=requires_condition,
        expiry_timing="target_turn_end",
    )


def _apply(state, *, requires_condition=None) -> list[str]:
    return apply_save_failure_effects(
        state, "monster-1", "test-cloud", [_effect(requires_condition=requires_condition)],
        round_number=1, range_ft=0,
    )


def test_action_spend_blocks_bonus_action_while_restricted() -> None:
    state = _state()
    assert _apply(state) == ["turn-restriction"]
    assert not is_available(state, "reaction")
    spend(state, "action")
    assert not is_available(state, "bonus_action")


def test_bonus_action_spend_blocks_action_while_restricted() -> None:
    state = _state()
    _apply(state)
    spend(state, "bonus_action")
    assert not is_available(state, "action")


def test_turn_refresh_does_not_bypass_active_restriction() -> None:
    state = _state()
    _apply(state)
    begin_turn(state)
    assert is_available(state, "action")
    assert is_available(state, "bonus_action")
    assert not is_available(state, "reaction")
    spend(state, "action")
    assert not is_available(state, "bonus_action")


def test_required_condition_prevents_ghost_restriction() -> None:
    state = _state()
    assert _apply(state, requires_condition="poisoned") == []
    assert is_available(state, "reaction")
    assert state.timed_effects == []


def test_required_condition_controls_restriction_lifetime() -> None:
    state = _state()
    state.active_effect_ids.append("poisoned")
    assert _apply(state, requires_condition="poisoned") == ["turn-restriction"]
    assert not is_available(state, "reaction")
    state.active_effect_ids.remove("poisoned")
    assert is_available(state, "reaction")
    spend(state, "action")
    assert is_available(state, "bonus_action")
