from __future__ import annotations

from app.combat.ability_checks import resolve_ability_check_outcome
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.domain.models import DiceRoll, RollMode


def test_level_fourteen_peerless_skill_uses_bardic_inspiration_on_failed_check() -> None:
    hero = build_lyra_silverstring_2014(14)
    state = build_combatant_state(hero)
    original = DiceRoll(
        notation="1d20+3",
        rolls=[7],
        selected_roll=7,
        modifier=3,
        total=10,
        mode=RollMode.NORMAL,
    )

    revised, succeeded = resolve_ability_check_outcome(
        state,
        "dexterity",
        original,
        16,
        dice=FixedDiceProvider([6]),
        round_number=1,
    )

    assert succeeded is True
    assert revised.total == 16
    assert revised.rolls == [7, 6]
    assert "Peerless Skill" in revised.notation
    resource = next(item for item in state.resources if item.id == "bardic-inspiration")
    assert resource.current_uses == 4


def test_peerless_skill_does_not_spend_on_already_successful_check() -> None:
    hero = build_lyra_silverstring_2014(14)
    state = build_combatant_state(hero)
    original = DiceRoll(
        notation="1d20+3",
        rolls=[13],
        selected_roll=13,
        modifier=3,
        total=16,
        mode=RollMode.NORMAL,
    )

    revised, succeeded = resolve_ability_check_outcome(
        state,
        "dexterity",
        original,
        16,
        dice=FixedDiceProvider([10]),
        round_number=1,
    )

    assert succeeded is True
    assert revised == original
    resource = next(item for item in state.resources if item.id == "bardic-inspiration")
    assert resource.current_uses == 5


def test_levels_fifteen_and_sixteen_preserve_single_lyra_progression() -> None:
    level15 = build_lyra_silverstring_2014(15)
    profile15 = build_lyra_silverstring_2014_profile(15)
    level16 = build_lyra_silverstring_2014(16)
    profile16 = build_lyra_silverstring_2014_profile(16)

    assert level15.d20_bonus_die_actions[0].dice_size == 12
    assert level15.ability_scores == profile15.final_ability_scores
    assert profile15.final_ability_scores.dexterity == 16

    assert level16.d20_bonus_die_actions[0].dice_size == 12
    assert level16.ability_scores == profile16.final_ability_scores
    assert profile16.final_ability_scores.dexterity == 18
    assert level16.armor_class == 15
    assert level16.weapon_attack.attack_bonus == 9
    assert level16.weapon_attack.damage_bonus == 4
