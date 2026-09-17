from app.combat.barbarian import (
    FRENZY_2014_EFFECT_ID,
    end_rage,
    enter_rage,
    extend_rage_from_attack,
    finalize_rage_turn,
    rage_active,
)
from app.combat.condition_rules import has_condition
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.barbarian_berserker_2014_profile import build_rokhan_stonefury_2014_profile
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.content.build_audit import audit_character_build
from app.domain.models import RollMode


def test_2014_berserker_levels_one_through_ten_are_real_2014_data() -> None:
    for level in range(1, 11):
        profile = build_rokhan_stonefury_2014_profile(level)
        hero = build_rokhan_stonefury_2014(level)
        assert hero.ruleset == profile.ruleset == "2014"
        assert hero.level == profile.level == level
        assert hero.ability_scores == profile.final_ability_scores
        assert hero.weapon_masteries == profile.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.source.startswith("D&D Basic Rules 2014")
        assert audit_character_build(profile, hero) == []


def test_2014_berserker_progression_breakpoints() -> None:
    level1 = build_rokhan_stonefury_2014(1)
    level2 = build_rokhan_stonefury_2014(2)
    level3 = build_rokhan_stonefury_2014(3)
    level5 = build_rokhan_stonefury_2014(5)
    level6 = build_rokhan_stonefury_2014(6)
    level7 = build_rokhan_stonefury_2014(7)
    level9 = build_rokhan_stonefury_2014(9)
    level10 = build_rokhan_stonefury_2014(10)

    assert {item.id: item.max_uses for item in level1.resources}["rage"] == 2
    assert {item.id: item.max_uses for item in level3.resources}["rage"] == 3
    assert {item.id: item.max_uses for item in level6.resources}["rage"] == 4
    assert level1.rage_damage_bonus == 2
    assert level9.rage_damage_bonus == 3
    assert level2.progression_features.reckless_attack is True
    assert level2.progression_features.danger_sense is True
    assert level3.progression_features.frenzy_bonus_attack_2014 is True
    assert level3.progression_features.frenzy is False
    assert len(level5.attack_action.slots) == 2
    assert level5.speed_ft == 40
    assert level6.progression_features.mindless_rage is True
    assert level7.progression_features.initiative_advantage is True
    assert level9.progression_features.melee_critical_extra_weapon_dice == 2
    assert level10.progression_features.intimidating_presence_2014 is True


def test_2014_handaxe_is_real_thrown_weapon_without_rage_damage_or_mastery() -> None:
    handaxe = build_rokhan_stonefury_2014(5).alternate_weapon_attacks[0]
    assert handaxe.weapon.name == "Handaxe"
    assert handaxe.weapon.dice_count == 1 and handaxe.weapon.dice_size == 6
    assert handaxe.weapon.normal_range_ft == 20 and handaxe.weapon.long_range_ft == 60
    assert handaxe.attack_ability == "strength"
    assert handaxe.rage_eligible is False
    assert handaxe.weapon.mastery_property is None


def test_half_orc_savage_attacks_and_brutal_critical_stack_as_weapon_dice() -> None:
    level1 = build_combatant_state(build_rokhan_stonefury_2014(1))
    roll1, components1 = resolve_weapon_damage(
        level1,
        level1.template.weapon_attack,
        FixedDiceProvider([1, 2, 3]),
        True,
        RollMode.NORMAL,
        "1:rokhan",
    )
    assert components1[0].notation == "3d12+3"
    assert roll1.total == 9

    level9 = build_combatant_state(build_rokhan_stonefury_2014(9))
    roll9, components9 = resolve_weapon_damage(
        level9,
        level9.template.weapon_attack,
        FixedDiceProvider([1, 2, 3, 4]),
        True,
        RollMode.NORMAL,
        "1:rokhan",
    )
    assert components9[0].notation == "4d12+5"
    assert roll9.total == 15


def test_2014_rage_ends_on_entry_turn_without_attack_or_damage() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(1))
    assert enter_rage(1, 1, state, "rokhan") is not None
    assert rage_active(state)
    finalize_rage_turn(2, 1, state, "rokhan")
    assert not rage_active(state)


def test_2014_rage_persists_when_the_barbarian_attacks() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(3))
    enter_rage(1, 1, state, "rokhan")
    extend_rage_from_attack(state, 1)
    finalize_rage_turn(2, 1, state, "rokhan")
    assert rage_active(state)
    assert FRENZY_2014_EFFECT_ID in state.active_effect_ids


def test_2014_mindless_rage_suspends_then_restores_existing_fear() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(6))
    state.active_effect_ids.append("frightened")
    assert has_condition(state, "frightened") is True

    enter_rage(1, 1, state, "rokhan")
    assert has_condition(state, "frightened") is False
    extend_rage_from_attack(state, 1)
    finalize_rage_turn(2, 1, state, "rokhan")
    assert has_condition(state, "frightened") is False

    end_rage(state)
    assert has_condition(state, "frightened") is True
    assert state.exhaustion_level_2014 == 1