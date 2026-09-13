from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.monster_catalog_2014 import MVP_CATALOG_PATH, monster_by_id_2014


def _state():
    return build_combatant_state(monster_by_id_2014("bandit", MVP_CATALOG_PATH))


def test_2014_poison_does_not_invent_arena_recovery_save() -> None:
    state = _state()
    apply_timed_condition(state, "poisoned", "source-a", source_effect_id="printed-poison")
    effect = state.timed_effects[0]
    assert effect.repeat_save_ability is None
    assert effect.repeat_save_dc is None
    assert effect.repeat_save_timing is None
    assert effect.expiry_timing is None


def test_2014_poison_preserves_printed_repeat_save_timing() -> None:
    state = _state()
    apply_timed_condition(
        state,
        "poisoned",
        "source-a",
        source_effect_id="printed-poison",
        applied_round=2,
        repeat_save_ability="constitution",
        repeat_save_dc=12,
        repeat_save_timing="target_turn_end",
    )
    effect = state.timed_effects[0]
    assert effect.repeat_save_ability == "constitution"
    assert effect.repeat_save_dc == 12
    assert effect.repeat_save_timing == "target_turn_end"


def test_distinct_2014_poison_effects_are_not_globally_deduplicated() -> None:
    state = _state()
    apply_timed_condition(state, "poisoned", "source-a", source_effect_id="poison-a")
    apply_timed_condition(state, "poisoned", "source-b", source_effect_id="poison-b")
    assert [(effect.source_id, effect.source_effect_id) for effect in state.timed_effects] == [
        ("source-a", "poison-a"),
        ("source-b", "poison-b"),
    ]
