from app.combat.action_economy import is_available, spend
from app.combat.d20_effects import strength_d20_disadvantage
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import _check_mode
from app.combat.modifier_stack import effective_speed
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_effect_rules import max_attacks_per_turn
from app.domain.models import EncounterSelection, RollMode


def _target():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    return setup.heroes[0]


def _slow(target) -> None:
    apply_timed_condition(
        target.state, "slowed", "copper-dragon",
        source_effect_id="slowing-breath", applied_round=1, expires_round=11,
        expiry_timing="target_turn_end", repeat_save_ability="constitution",
        repeat_save_dc=14, repeat_save_timing="target_turn_end",
        speed_multiplier=0.5, blocks_reactions=True,
        action_bonus_exclusive=True, max_attacks_per_turn=1,
    )


def _weaken(target) -> None:
    apply_timed_condition(
        target.state, "weakened-strength", "gold-dragon",
        source_effect_id="weakening-breath", applied_round=1, expires_round=11,
        expiry_timing="target_turn_end", repeat_save_ability="strength",
        repeat_save_dc=14, repeat_save_timing="target_turn_end",
        disadvantage_strength_d20_tests=True,
    )


def test_slowing_breath_halves_speed_and_blocks_reactions() -> None:
    target = _target()
    base_speed = target.state.template.speed_ft
    _slow(target)
    assert effective_speed(target.state) == base_speed // 2
    assert is_available(target.state, "reaction") is False
    assert max_attacks_per_turn(target.state) == 1


def test_slowing_breath_allows_action_or_bonus_action_not_both() -> None:
    target = _target()
    _slow(target)
    assert is_available(target.state, "action") is True
    assert is_available(target.state, "bonus_action") is True
    spend(target.state, "action")
    assert is_available(target.state, "bonus_action") is False


def test_weakening_breath_penalizes_strength_d20_tests_only() -> None:
    target = _target()
    _weaken(target)
    assert strength_d20_disadvantage(target.state) == 1
    assert saving_throw_mode(target.state, "strength") is RollMode.DISADVANTAGE
    assert saving_throw_mode(target.state, "dexterity") is RollMode.NORMAL
    assert _check_mode(target.state, True) is RollMode.DISADVANTAGE
    assert _check_mode(target.state, False) is RollMode.NORMAL
