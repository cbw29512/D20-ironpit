from app.combat.action_economy import spend
from app.combat.action_surge import action_surge_available, use_action_surge
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.state import build_combatant_state
from app.combat.tactical_mind import apply_tactical_mind
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.level_resources import fighter_action_surge_uses, fixed_class_hit_points
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DiceRoll


def _member(template, combatant_id, side, position):
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_fighter_level_two_snapshot_has_raw_hp_and_resources() -> None:
    karnok = build_karnok_stoneward_level(2)
    assert karnok.max_hp == fixed_class_hit_points(2, 10, 2) == 20
    assert {item.id: item.max_uses for item in karnok.resources} == {
        "second-wind": 2,
        "action-surge": 1,
        "adrenaline-rush": 2,
        "relentless-endurance": 1,
    }
    assert fighter_action_surge_uses(1) == 0
    assert fighter_action_surge_uses(2) == 1
    assert fighter_action_surge_uses(16) == 1
    assert fighter_action_surge_uses(17) == 2


def test_action_surge_grants_one_additional_action_and_spends_one_use() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(2))
    spend(state, "action")
    event = use_action_surge(1, 1, "hero-1", state, "1:hero-1")
    assert state.action_available is True
    assert next(item for item in state.resources if item.id == "action-surge").current_uses == 0
    assert event.feature_id == "action-surge"
    assert event.resource_remaining == 0


def test_action_surge_is_limited_to_once_per_turn_even_with_two_uses() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(2))
    resource = next(item for item in state.resources if item.id == "action-surge")
    resource.current_uses = resource.max_uses = 2
    spend(state, "action")
    use_action_surge(1, 1, "hero-1", state, "1:hero-1")
    spend(state, "action")
    assert action_surge_available(state, "1:hero-1") is False
    assert action_surge_available(state, "2:hero-1") is True


def test_action_surge_ai_uses_extra_action_for_immediate_legal_attack() -> None:
    hero = _member(build_karnok_stoneward_level(2), "hero-1", "heroes", 0)
    target_template = build_commoner().model_copy(update={"max_hp": 100})
    target = _member(target_template, "monster-1", "monsters", 5)
    setup = EncounterSetup(heroes=[hero], monsters=[target], hero_total_levels=2, monster_total_cr="0")
    spend(hero.state, "action")
    events, _ = resolve_action_surge_attack(
        1, 1, hero, setup, FixedDiceProvider([10, 1, 1, 1, 1]), "1:hero-1",
    )
    assert [event.feature_id for event in events] == ["action-surge", "action-surge"]
    assert events[1].event_type == "attack"
    assert hero.state.action_available is False


def _failed_check(total: int) -> DiceRoll:
    return DiceRoll(notation="1d20", rolls=[total - 5], selected_roll=total - 5, modifier=5, total=total)


def test_tactical_mind_spends_second_wind_only_when_it_turns_failure_into_success() -> None:
    success_state = build_combatant_state(build_karnok_stoneward_level(2))
    success_roll, used, succeeded = apply_tactical_mind(
        success_state, _failed_check(10), 15, FixedDiceProvider([5]),
    )
    assert used is True and succeeded is True and success_roll.total == 15
    assert next(item for item in success_state.resources if item.id == "second-wind").current_uses == 1

    failure_state = build_combatant_state(build_karnok_stoneward_level(2))
    failure_roll, used, succeeded = apply_tactical_mind(
        failure_state, _failed_check(10), 15, FixedDiceProvider([1]),
    )
    assert used is True and succeeded is False and failure_roll.total == 11
    assert next(item for item in failure_state.resources if item.id == "second-wind").current_uses == 2
