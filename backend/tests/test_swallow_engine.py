from __future__ import annotations

from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple
from app.combat.pit_policy import choose_standard_attack, target_order
from app.combat.state import build_combatant_state
from app.combat.swallow import resolve_swallow, resolve_swallow_turn_end
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize
from app.domain.swallow import SwallowAction


def _setup(action: SwallowAction) -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    hero_template = build_karnok_stoneward()
    monster_template = build_goblin_warrior()
    monster_template = monster_template.model_copy(update={"swallow_actions": [action]})
    hero = EncounterCombatant(
        combatant_id="hero-1", side="heroes", position_ft=5,
        state=build_combatant_state(hero_template),
    )
    monster = EncounterCombatant(
        combatant_id="monster-1", side="monsters", position_ft=5,
        state=build_combatant_state(monster_template),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[monster], hero_total_levels=1, monster_total_cr="1/4",
    )
    apply_grapple(hero.state, monster.combatant_id, 11, 5)
    return setup, monster, hero


def test_delayed_swallow_disgorges_prone_after_first_tick() -> None:
    base = build_goblin_warrior()
    action = SwallowAction(
        id="test-frog-swallow", max_target_size=CreatureSize.MEDIUM,
        damage_dice_count=2, damage_dice_size=4, first_tick_delay_rounds=1,
        disgorge_after_first_tick=True,
        forbidden_attack_ids_while_active=[base.weapon_attack.id],
    )
    setup, source, target = _setup(action)

    event = resolve_swallow(1, 1, source, target, action, setup)

    assert event.applied_condition_ids == ["blinded", "restrained"]
    assert target.state.grapple_sources == []
    assert has_condition(target.state, "blinded") is True
    assert has_condition(target.state, "restrained") is True
    assert target_order(source, setup) == []
    assert target_order(target, setup) == [source]
    assert choose_standard_attack(source, setup) is None

    events, sequence = resolve_swallow_turn_end(2, 1, source, setup, FixedDiceProvider([1]))
    assert (events, sequence, target.state.current_hp) == ([], 2, target.state.template.max_hp)

    events, sequence = resolve_swallow_turn_end(2, 2, source, setup, FixedDiceProvider([2, 3]))
    assert sequence == 3
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 5
    assert target.state.swallowed is None
    assert has_condition(target.state, "blinded") is False
    assert has_condition(target.state, "restrained") is False
    assert "prone" in target.state.active_effect_ids


def test_recurring_swallow_ticks_immediately_and_stays_active() -> None:
    action = SwallowAction(
        id="test-toad-swallow", max_target_size=CreatureSize.MEDIUM,
        damage_dice_count=3, damage_dice_size=6, first_tick_delay_rounds=0,
        disgorge_after_first_tick=False,
    )
    setup, source, target = _setup(action)

    resolve_swallow(1, 1, source, target, action, setup)
    events, sequence = resolve_swallow_turn_end(2, 1, source, setup, FixedDiceProvider([3, 3, 4]))

    assert sequence == 3
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 10
    assert target.state.current_hp == target.state.template.max_hp - 10
    assert target.state.swallowed is not None
    assert has_condition(target.state, "blinded") is True
    assert has_condition(target.state, "restrained") is True
