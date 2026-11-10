"""Actual 2014 no-save Sleep casts across innate and prepared monster sources."""
from __future__ import annotations

import pytest

from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.hit_point_pool_spell_policy import choose_hp_pool_spell
from app.combat.hit_point_pool_spell_resolution import resolve_hp_pool_spell
from app.combat.pit_policy import target_order
from app.combat.timed_conditions import apply_timed_condition
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _encounter(monster_id: str, *, hp: int = 7, target_count: int = 1):
    source = next(card for card in load_monster_source_2014() if card.id == monster_id)
    caster_template = compile_combatant(adapt_monster_mechanics_2014(source))
    caster = EncounterCombatant(
        combatant_id="caster", side="monsters", position_ft=0,
        state=build_combatant_state(caster_template),
    )
    target_template = build_commoner().model_copy(update={
        "max_hp": hp, "ruleset": "2014", "creature_type": "humanoid",
    })
    targets = [
        EncounterCombatant(
            combatant_id=f"hero-{index}", side="heroes", position_ft=30,
            state=build_combatant_state(target_template),
        ) for index in range(target_count)
    ]
    setup = EncounterSetup(
        heroes=targets, monsters=[caster],
        hero_total_levels=target_count, monster_total_cr="5", ruleset="2014",
    )
    return caster, targets, setup


@pytest.mark.parametrize("monster_id", ["dust-mephit", "night-hag", "oni", "spirit-naga"])
def test_all_four_printed_casters_cast_real_sleep(monster_id):
    caster, targets, setup = _encounter(monster_id)
    action, = caster.state.template.hit_point_pool_spell_actions
    assert action.name == "Sleep"
    assert (action.pool_dice_count, action.pool_dice_size) == (5, 8)
    before_hp = targets[0].state.current_hp
    choice = choose_hp_pool_spell(caster, setup, "1:caster")
    assert choice is not None
    assert choice.action == action
    events, seq = resolve_hp_pool_spell(
        1, 1, caster, setup, choice, "1:caster", FixedDiceProvider([8] * 60),
    )
    assert seq == len(events) + 1
    assert events[0].feature_id == "sleep"
    assert events[0].feature_roll is not None
    assert events[0].feature_roll.total >= 40
    assert caster.state.action_available is False
    assert targets[0].state.current_hp == before_hp
    assert has_condition(targets[0].state, "unconscious", setup=setup)
    effect, = [effect for effect in targets[0].state.timed_effects if effect.effect_id == "unconscious"]
    assert effect.ends_on_damage is True
    assert "wake-sleeper" in effect.allowed_removal_action_ids
    assert effect.source_effect_id == "sleep"
    assert effect.expires_round == 11
    if choice.alternate_cast is not None and choice.alternate_cast.resource_id:
        resource = next(item for item in caster.state.resources if item.id == choice.alternate_cast.resource_id)
        assert resource.current_uses == resource.max_uses - 1
        assert caster.state.spell_slot_expended_turn_key is None
    elif choice.alternate_cast is None:
        resource = next(item for item in caster.state.resources if item.id == f"spell-slot-{choice.slot_level}")
        assert resource.current_uses == resource.max_uses - 1
        assert caster.state.spell_slot_expended_turn_key == "1:caster"


def test_hp_pool_is_lowest_hp_first_and_does_not_damage():
    caster, targets, setup = _encounter("night-hag", hp=8, target_count=2)
    targets[0].state.current_hp = 8
    targets[1].state.current_hp = 2
    choice = choose_hp_pool_spell(caster, setup, "1:caster")
    assert choice is not None
    events, _ = resolve_hp_pool_spell(1, 1, caster, setup, choice, "1:caster",
                                     FixedDiceProvider([1] * 60))
    assert [ev.target_id for ev in events if ev.target_id] == ["hero-1"]
    assert [item.state.current_hp for item in targets] == [8, 2]


def test_undead_and_charm_immune_targets_are_not_put_to_sleep():
    for kind, immunities in [("undead", []), ("humanoid", ["charmed"])]:
        caster, targets, setup = _encounter("night-hag")
        targets[0].state.template = targets[0].state.template.model_copy(update={
            "creature_type": kind, "condition_immunities": immunities,
        })
        assert choose_hp_pool_spell(caster, setup, "1:caster") is None


def test_existing_unconscious_is_not_selected_again():
    caster, targets, setup = _encounter("night-hag")
    targets[0].state.active_effect_ids.append("unconscious")
    assert choose_hp_pool_spell(caster, setup, "1:caster") is None


def test_damage_wakes_the_sleeping_target_and_targeting_resumes():
    caster, targets, setup = _encounter("night-hag", hp=9, target_count=2)
    choice = choose_hp_pool_spell(caster, setup, "1:caster")
    assert choice is not None
    resolve_hp_pool_spell(1, 1, caster, setup, choice, "1:caster",
                          FixedDiceProvider([8] * 60))
    assert all(has_condition(member.state, "unconscious") for member in targets)
    assert len(target_order(caster, setup)) == 2, "all slept targets remain attackable"
    apply_damage(targets[0].state, 1, affected_states=[m.state for m in targets])
    assert not has_condition(targets[0].state, "unconscious")
    assert has_condition(targets[1].state, "unconscious")
    assert [m.combatant_id for m in target_order(caster, setup)] == ["hero-0"]


def test_synthetic_rename_does_not_change_spell_mechanics():
    source = next(card for card in load_monster_source_2014() if card.id == "night-hag")
    renamed = source.model_copy(update={"id": "renamed-source", "name": "Unrelated Caster"})
    original = compile_combatant(adapt_monster_mechanics_2014(source))
    same = compile_combatant(adapt_monster_mechanics_2014(renamed))
    assert same.hit_point_pool_spell_actions == original.hit_point_pool_spell_actions

def test_sleep_target_is_deferred_even_behind_other_incapacitated_foes():
    caster, targets, setup = _encounter("night-hag", hp=10, target_count=2)
    apply_timed_condition(
        targets[0].state, "unconscious", caster.combatant_id,
        source_effect_id="synthetic-sleep", applied_round=1,
        expires_round=11, expiry_timing="source_turn_start",
        ends_on_damage=True, use_default_poison_recovery=False,
    )
    targets[1].state.active_effect_ids.append("stunned")
    assert [member.combatant_id for member in target_order(caster, setup)] == ["hero-1"]
