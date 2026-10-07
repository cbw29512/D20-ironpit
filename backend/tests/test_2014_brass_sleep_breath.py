from __future__ import annotations

from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.condition_rules import condition_speed_is_zero, is_incapacitated
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import TimedEffect

_EXPECTED = {
    "brass-dragon-wyrmling": (11, 15, 10),
    "young-brass-dragon": (14, 30, 50),
    "adult-brass-dragon": (18, 60, 100),
}


def _source(monster_id: str):
    try:
        return next(item for item in load_monster_source_2014() if item.id == monster_id)
    except Exception:
        raise


def _compile(monster_id: str):
    try:
        return compile_combatant(adapt_basic_monster_2014(_source(monster_id)))
    except Exception:
        raise


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    try:
        state = build_combatant_state(template.model_copy(deep=True))
        state.position = GridPosition(x=x, y=0)
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=x * 5,
            state=state,
        )
    except Exception:
        raise


def test_brass_sleep_breath_family_binds_existing_save_timed_condition_and_recharge() -> None:
    for monster_id, (dc, cone_ft, duration_rounds) in _EXPECTED.items():
        source = _source(monster_id)
        assert basic_blockers_2014(source) == ()

        template = _compile(monster_id)
        sleep = next(action for action in template.saving_throw_actions if action.id == "sleep-breath")
        fire = next(action for action in template.saving_throw_actions if action.id == "fire-breath")

        assert sleep.name == "Sleep Breath"
        assert (sleep.save_ability, sleep.dc) == ("constitution", dc)
        assert sleep.area is not None
        assert (sleep.area.shape, sleep.area.length_ft) == ("cone", cone_ft)
        assert sleep.resource_id == fire.resource_id == "breath-weapons"

        rider = sleep.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "unconscious"
        assert rider.duration_rounds == duration_rounds
        assert rider.ends_on_damage is True
        assert rider.allowed_removal_action_ids == ["wake-sleeper"]

        recharge = next(rule for rule in template.recharge_rules if rule.resource_id == "breath-weapons")
        assert recharge.minimum_roll == 5

    assert "mechanic:save-action" not in basic_blockers_2014(_source("ancient-brass-dragon"))


def test_wyrmling_sleep_breath_uses_universal_unconscious_and_wake_action() -> None:
    dragon = _member(_compile("brass-dragon-wyrmling"), "monster:brass-wyrmling", "monsters", 0)
    commoner = _compile("commoner")
    helper = _member(commoner, "hero:helper", "heroes", 1)
    sleeper = _member(commoner, "hero:sleeper", "heroes", 2)
    setup = EncounterSetup(
        heroes=[helper, sleeper],
        monsters=[dragon],
        hero_total_levels=2,
        monster_total_cr="1",
        ruleset="2014",
        map_definition=BattleMapDefinition(id="brass-sleep", width_squares=12, height_squares=12),
    )

    sleep = next(action for action in dragon.state.template.saving_throw_actions if action.id == "sleep-breath")
    event = resolve_save_action(
        1,
        1,
        dragon,
        sleeper,
        sleep,
        10,
        FixedDiceProvider([1]),
        affected_states=[helper.state, sleeper.state, dragon.state],
        setup=setup,
    )

    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["unconscious"]
    effect = next(item for item in sleeper.state.timed_effects if item.effect_id == "unconscious")
    assert effect.ends_on_damage is True
    assert effect.allowed_removal_action_ids == ["wake-sleeper"]
    assert is_incapacitated(sleeper.state) is True
    assert condition_speed_is_zero(sleeper.state) is True
    assert "prone" in sleeper.state.active_effect_ids

    choice = choose_condition_removal_action(helper, setup, "1:hero:helper")
    assert choice is not None
    wake, target, conditions = choice
    assert wake.id == "wake-sleeper"
    assert target is sleeper
    assert conditions == ["unconscious"]

    wake_event = resolve_condition_removal(
        2, 1, helper, target, wake, conditions, "1:hero:helper",
    )
    assert helper.state.action_available is False
    assert wake_event.feature_id == "wake-sleeper"
    assert "unconscious" not in sleeper.state.active_effect_ids
    assert "prone" in sleeper.state.active_effect_ids
    assert not any(item.effect_id == "unconscious" for item in sleeper.state.timed_effects)
    assert is_incapacitated(sleeper.state) is False

    helper.state.action_available = True
    sleeper.state.active_effect_ids.append("unconscious")
    sleeper.state.timed_effects.append(TimedEffect(
        effect_id="unconscious",
        source_id="other-effect",
    ))
    assert choose_condition_removal_action(helper, setup, "1:hero:helper") is None
