from app.combat.spellcasting import (
    mark_spell_cast,
    mark_slot_spell_cast,
    spell_cast_available,
    slot_spell_available,
)
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014


def test_2014_bonus_action_spell_allows_only_one_action_cantrip_afterward() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014(3))
    turn_key = "1:cleric"

    mark_slot_spell_cast(
        state, turn_key, spell_level=2, action_cost="bonus_action",
    )

    assert state.spell_slot_expended_turn_key is None
    assert state.bonus_action_spell_cast_turn_key == turn_key
    assert state.non_action_cantrip_spell_cast_turn_key == turn_key
    assert spell_cast_available(
        state, turn_key, 0, "action", expends_spell_slot=False,
    )
    assert not spell_cast_available(
        state, turn_key, 1, "action", expends_spell_slot=True,
    )
    assert not spell_cast_available(
        state, turn_key, 1, "reaction", expends_spell_slot=True,
    )


def test_2014_action_spell_blocks_later_bonus_action_spell_but_not_second_action_spell() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014(3))
    turn_key = "1:cleric"

    mark_slot_spell_cast(
        state, turn_key, spell_level=1, action_cost="action",
    )

    assert state.bonus_action_spell_cast_turn_key is None
    assert state.non_action_cantrip_spell_cast_turn_key == turn_key
    assert slot_spell_available(
        state, turn_key, spell_level=2, action_cost="action",
    )
    assert not slot_spell_available(
        state, turn_key, spell_level=1, action_cost="bonus_action",
    )


def test_2024_one_slot_spell_per_turn_is_independent_of_free_casts_and_cantrips() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_level(3))
    turn_key = "1:cleric"

    mark_slot_spell_cast(
        state, turn_key, spell_level=1, action_cost="action",
    )

    assert state.spell_slot_expended_turn_key == turn_key
    assert not slot_spell_available(
        state, turn_key, spell_level=2, action_cost="bonus_action",
    )
    assert spell_cast_available(
        state, turn_key, 0, "action", expends_spell_slot=False,
    )
    assert spell_cast_available(
        state, turn_key, 2, "action", expends_spell_slot=False,
    )


def test_2014_reaction_spell_on_a_different_creatures_turn_uses_a_different_turn_key() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014(3))
    mark_spell_cast(
        state, "1:cleric", 1, "bonus_action", expends_spell_slot=True,
    )

    assert spell_cast_available(
        state, "1:enemy", 1, "reaction", expends_spell_slot=True,
    )
