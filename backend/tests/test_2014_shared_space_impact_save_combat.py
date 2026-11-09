"""Real shared-save damage and Prone resolution from an immutable 2014 card."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    card = next(
        row for row in load_monster_source_2014() if row.id == "air-elemental"
    )
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    owner = EncounterCombatant(
        combatant_id="source", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    heroes = [
        EncounterCombatant(
            combatant_id=f"target-{index}", side="heroes", position_ft=0,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"name": f"Target {index}"})
            ),
        )
        for index in range(2)
    ]
    encounter = EncounterSetup(
        heroes=heroes, monsters=[owner], ruleset="2014",
        hero_total_levels=1, monster_total_cr="5",
    )
    (action,) = [save for save in template.saving_throw_actions if save.id == "whirlwind"]
    return owner, heroes, encounter, action


def test_real_card_failed_save_deals_full_damage_and_prone_without_fling():
    source, (target, _), setup, action = _setup()
    before = target.state.current_hp
    positions = (source.position_ft, target.position_ft)
    event = resolve_save_action(
        1, 1, source, target, action, 0,
        FixedDiceProvider([1, 2, 2, 2]), spend_action=False,
        check_resource=False, spend_resource=False, setup=setup,
    )
    assert event.save_succeeded is False
    assert event.hp_before == before
    assert event.hp_after < before
    assert "prone" in target.state.active_effect_ids
    assert "prone" in event.applied_condition_ids
    assert (source.position_ft, target.position_ft) == positions
    assert event.feature_id == "whirlwind"
    assert "Whirlwind" in event.description


def test_real_card_success_half_damage_no_prone_and_no_forced_movement():
    source, (_, target), setup, action = _setup()
    positions = (source.position_ft, target.position_ft)
    before = target.state.current_hp
    event = resolve_save_action(
        1, 1, source, target, action, 0,
        FixedDiceProvider([20, 2, 2, 2]), spend_action=False,
        check_resource=False, spend_resource=False, setup=setup,
    )
    assert event.save_succeeded is True
    assert before - target.state.current_hp >= 0
    assert "prone" not in target.state.active_effect_ids
    assert "prone" not in event.applied_condition_ids
    assert (source.position_ft, target.position_ft) == positions
