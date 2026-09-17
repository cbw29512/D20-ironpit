from app.combat.dice import FixedDiceProvider
from app.combat.indomitable import use_indomitable
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014


def test_2014_champion_levels_one_through_ten_stay_in_2014_rules() -> None:
    for level in range(1, 11):
        hero = build_karnok_stoneward_2014(level)
        assert hero.ruleset == "2014"
        assert hero.level == level
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.source.startswith("D&D Basic Rules 2014")


def test_2014_champion_progression_changes_only_at_legal_levels() -> None:
    level1 = build_karnok_stoneward_2014(1)
    level3 = build_karnok_stoneward_2014(3)
    level5 = build_karnok_stoneward_2014(5)
    level7 = build_karnok_stoneward_2014(7)
    level9 = build_karnok_stoneward_2014(9)
    level10 = build_karnok_stoneward_2014(10)

    assert level1.progression_features.critical_hit_minimum == 20
    assert level3.progression_features.critical_hit_minimum == 19
    assert len(level1.attack_action.slots) == 1
    assert len(level5.attack_action.slots) == 2
    assert level7.initiative_bonus == 4
    assert level7.skill_bonuses["acrobatics"] == 4
    assert level9.progression_features.indomitable_reroll is True
    assert level9.progression_features.indomitable_bonus == 0
    assert "Archery" not in level9.fighting_styles
    assert "Archery" in level10.fighting_styles
    assert level10.alternate_weapon_attacks[0].attack_bonus == 8


def test_2014_indomitable_rerolls_without_2024_level_bonus() -> None:
    state = build_combatant_state(build_karnok_stoneward_2014(9))
    roll = use_indomitable(state, "wisdom", FixedDiceProvider([10]))

    assert roll is not None
    assert roll.selected_roll == 10
    assert roll.total == 11
    assert "Indomitable]" in roll.notation
    assert "+9" not in roll.notation
    resource = next(item for item in state.resources if item.id == "indomitable")
    assert resource.current_uses == 0


def test_2014_level_ten_has_no_2024_champion_features() -> None:
    hero = build_karnok_stoneward_2014(10)
    progression = hero.progression_features

    assert progression.initiative_advantage is False
    assert progression.athletics_advantage is False
    assert progression.heroic_warrior is False
    assert progression.tactical_master_sap_weapon_ids == []
    assert progression.tactical_shift_fraction == 0.0
    assert progression.critical_move_fraction == 0.0
