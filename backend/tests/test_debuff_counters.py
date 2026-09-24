from app.combat.debuff_counters import difficult_terrain_multiplier
from app.combat.grapple import apply_grapple
from app.combat.modifier_stack import add_modifier, effective_speed
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.paladin_devotion_2014_spells import freedom_of_movement_2014
from app.content.roster import build_arena_roster
from app.domain.debuffs import DebuffCounter
from app.domain.modifiers import CombatModifier, ModifierKind


def _state():
    roster = build_arena_roster()
    template = next(item for item in roster.characters if item.id == "karnok-stoneward-l1").model_copy(deep=True)
    return build_combatant_state(template)


def _counter(state, index: int, counter: DebuffCounter) -> None:
    add_modifier(state, CombatModifier(
        id=f"buff:{index}",
        source_id="buff-source",
        source_effect_id="test-buff",
        kind=ModifierKind.DEBUFF_COUNTER,
        debuff_counter=counter,
    ))


def test_magical_condition_counter_does_not_block_nonmagical_condition() -> None:
    magical = _state()
    _counter(magical, 1, DebuffCounter(debuff_id="paralyzed", source_scope="magical"))
    assert apply_timed_condition(
        magical,
        "paralyzed",
        "spell-source",
        source_is_magical=True,
        use_default_poison_recovery=False,
    ) is None

    nonmagical = _state()
    _counter(nonmagical, 1, DebuffCounter(debuff_id="paralyzed", source_scope="magical"))
    assert apply_timed_condition(
        nonmagical,
        "paralyzed",
        "monster-source",
        source_is_magical=False,
        use_default_poison_recovery=False,
    ) == "paralyzed"


def test_magical_speed_reduction_counter_preserves_speed_only_for_magical_debuff() -> None:
    magical = _state()
    _counter(magical, 1, DebuffCounter(debuff_id="speed-reduction", source_scope="magical"))
    add_modifier(magical, CombatModifier(
        id="magical-slow",
        source_id="spell-source",
        source_effect_id="slow",
        source_is_magical=True,
        kind=ModifierKind.SPEED,
        flat_bonus=-10,
    ))
    assert effective_speed(magical) == magical.template.speed_ft

    nonmagical = _state()
    _counter(nonmagical, 1, DebuffCounter(debuff_id="speed-reduction", source_scope="magical"))
    add_modifier(nonmagical, CombatModifier(
        id="nonmagical-slow",
        source_id="terrain-source",
        source_effect_id="hampered",
        source_is_magical=False,
        kind=ModifierKind.SPEED,
        flat_bonus=-10,
    ))
    assert effective_speed(nonmagical) == nonmagical.template.speed_ft - 10


def test_nonmagical_grapple_counter_spends_five_feet_and_clears_grapple() -> None:
    state = _state()
    _counter(state, 1, DebuffCounter(
        debuff_id="grappled",
        source_scope="nonmagical",
        mode="remove-with-movement",
        movement_cost_ft=5,
    ))
    _counter(state, 2, DebuffCounter(
        debuff_id="restrained",
        source_scope="nonmagical",
        mode="remove-with-movement",
        movement_cost_ft=5,
    ))
    assert apply_grapple(state, "crocodile", 12, 5, restrains=True) == ["grappled", "restrained"]

    resolved = begin_turn(state)

    assert resolved == [("restrained", "crocodile", 5)]
    assert state.grapple_sources == []
    assert "grappled" not in state.active_effect_ids
    assert "restrained" not in state.active_effect_ids
    assert state.movement_remaining_ft == state.template.speed_ft - 5


def test_magical_speed_counter_neutralizes_magical_grapple_speed_zero_without_removing_grapple() -> None:
    state = _state()
    _counter(state, 1, DebuffCounter(debuff_id="speed-reduction", source_scope="magical"))
    apply_grapple(state, "magic-source", 12, 5, source_is_magical=True)

    resolved = begin_turn(state)

    assert resolved == []
    assert len(state.grapple_sources) == 1
    assert state.movement_remaining_ft == state.template.speed_ft


def test_nonmagical_grapple_counter_does_not_clear_magical_grapple() -> None:
    state = _state()
    _counter(state, 1, DebuffCounter(
        debuff_id="grappled",
        source_scope="nonmagical",
        mode="remove-with-movement",
        movement_cost_ft=5,
    ))
    apply_grapple(state, "magic-source", 12, 5, source_is_magical=True)

    resolved = begin_turn(state)

    assert resolved == []
    assert len(state.grapple_sources) == 1
    assert state.movement_remaining_ft == 0


def test_difficult_terrain_is_a_counterable_debuff() -> None:
    state = _state()
    assert difficult_terrain_multiplier(state) == 2
    _counter(state, 1, DebuffCounter(debuff_id="difficult-terrain"))
    assert difficult_terrain_multiplier(state) == 1


def test_freedom_of_movement_is_data_composed_from_universal_counters() -> None:
    spell = freedom_of_movement_2014()
    counters = [effect.debuff_counter for effect in spell.modifier_effects]

    assert spell.level == 4
    assert spell.duration_minutes == 60
    assert spell.concentration is False
    assert all(counter is not None for counter in counters)
    signatures = {
        (counter.debuff_id, counter.source_scope, counter.mode, counter.movement_cost_ft)
        for counter in counters
        if counter is not None
    }
    assert ("difficult-terrain", "any", "prevent", 0) in signatures
    assert ("speed-reduction", "magical", "prevent", 0) in signatures
    assert ("paralyzed", "magical", "prevent", 0) in signatures
    assert ("restrained", "magical", "prevent", 0) in signatures
    assert ("grappled", "nonmagical", "remove-with-movement", 5) in signatures
    assert ("restrained", "nonmagical", "remove-with-movement", 5) in signatures
