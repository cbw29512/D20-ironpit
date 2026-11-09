"""Integration coverage for source-bound Whelm using generic save/Grapple state.

The monster is deliberately not admitted until its complete printed Action
(including breathing, successful exit and rescue) is implemented.
"""
from __future__ import annotations

from app.combat.grapple import release_grapple
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.saving_throw_effects import apply_save_effects
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize


def _encounter(*sizes: CreatureSize):
    source = next(
        item for item in load_monster_source_2014()
        if item.id == "water-elemental"
    )
    owner = EncounterCombatant(
        combatant_id="source", side="monsters", position_ft=0,
        state=build_combatant_state(
            compile_combatant(adapt_monster_mechanics_2014(source))
        ),
    )
    targets = []
    for index, size in enumerate(sizes):
        hero = build_demo_fighter().model_copy(
            update={"name": f"target-{index}", "size": size},
        )
        targets.append(EncounterCombatant(
            combatant_id=f"target-{index}",
            side="heroes", position_ft=0,
            state=build_combatant_state(hero),
        ))
    setup = EncounterSetup(
        heroes=targets, monsters=[owner], ruleset="2014",
        hero_total_levels=1, monster_total_cr="5",
    )
    (action,) = [
        save for save in owner.state.template.saving_throw_actions
        if save.id == "whelm"
    ]
    return owner, targets, setup, action


def test_printed_water_save_reuses_generic_size_and_capacity_state():
    owner, (large, medium, huge), setup, action = _encounter(
        CreatureSize.LARGE, CreatureSize.MEDIUM, CreatureSize.HUGE,
    )
    # A huge creature is still eligible for the DAMAGE save; only the
    # printed failed-save Grapple is size-limited.
    assert action.target_max_size is None
    assert action.grapple_max_target_size == CreatureSize.LARGE
    huge_result = apply_save_effects(
        owner, huge, action, False, None, 1, setup=setup,
    )
    assert huge_result.applied_conditions == []
    assert huge.state.grapple_sources == []

    large_result = apply_save_effects(
        owner, large, action, False, None, 1, setup=setup,
    )
    assert large_result.applied_conditions == ["grappled", "restrained"]
    assert large.state.grapple_sources[0].prevents_breathing

    # One Large uses the full two-slot capacity; a valid save may still
    # deal printed damage, but it cannot apply a third Grapple.
    assert apply_save_effects(
        owner, medium, action, False, None, 1, setup=setup,
    ).applied_conditions == []
    assert medium.state.grapple_sources == []
    release_grapple(large.state, owner.combatant_id)
    assert apply_save_effects(
        owner, medium, action, False, None, 1, setup=setup,
    ).applied_conditions == ["grappled", "restrained"]


def test_success_does_not_apply_grapple_and_leaves_state_unchanged():
    owner, (medium,), setup, action = _encounter(CreatureSize.MEDIUM)
    prior = (owner.position_ft, medium.position_ft)
    result = apply_save_effects(
        owner, medium, action, True, None, 1, setup=setup,
    )
    assert result.applied_conditions == []
    assert medium.state.grapple_sources == []
    assert (owner.position_ft, medium.position_ft) == prior


def test_real_source_success_logs_whelm_exit_with_no_relocation():
    source, (victim,), setup, action = _encounter(CreatureSize.MEDIUM)
    assert action.successful_save_exits_source_space
    before_positions = (source.position_ft, victim.position_ft)
    before_hp = victim.state.current_hp
    event = resolve_save_action(
        1, 1, source, victim, action, 0,
        FixedDiceProvider([20]),
        spend_action=False, check_resource=False, spend_resource=False,
        setup=setup,
    )
    assert event.save_succeeded
    assert event.hp_after == before_hp
    assert event.applied_condition_ids == []
    assert "pushed out of" in event.description
    assert "position unchanged by arena rule" in event.description
    assert "Whelm" in event.description
    assert (source.position_ft, victim.position_ft) == before_positions
