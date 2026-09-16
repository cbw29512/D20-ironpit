from app.combat.dice import FixedDiceProvider
from app.combat.indomitable import use_indomitable
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_2014 import build_karnok_stoneward_2014_level


def _resources(level: int) -> dict[str, int]:
    template = build_karnok_stoneward_2014_level(level)
    return {item.id: item.max_uses for item in template.resources}


def test_2014_champion_is_contiguous_and_never_exports_weapon_mastery() -> None:
    for level in range(1, 11):
        template = build_karnok_stoneward_2014_level(level)
        assert template.ruleset == "2014"
        assert template.level == level
        assert template.weapon_masteries == []
        assert template.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in template.alternate_weapon_attacks)
        assert build_certified_hero_registry()[("fighter", level, "canonical-2014")] == (
            "Karnok Stoneward", f"fighter-2014-canonical-l{level}",
        )


def test_2014_fighter_progression_matches_level_gates() -> None:
    level1 = build_karnok_stoneward_2014_level(1)
    level3 = build_karnok_stoneward_2014_level(3)
    level5 = build_karnok_stoneward_2014_level(5)
    level7 = build_karnok_stoneward_2014_level(7)
    level10 = build_karnok_stoneward_2014_level(10)

    assert _resources(1) == {"second-wind": 1}
    assert _resources(2) == {"second-wind": 1, "action-surge": 1}
    assert level1.progression_features.critical_hit_minimum == 20
    assert level3.progression_features.critical_hit_minimum == 19
    assert level5.attack_action is not None and len(level5.attack_action.slots) == 2
    assert level7.initiative_bonus == 4
    assert level7.skill_bonuses["acrobatics"] == 4
    assert _resources(9) == {"second-wind": 1, "action-surge": 1, "indomitable": 1}
    assert level10.fighting_styles == ["Defense", "Archery"]
    assert level10.alternate_weapon_attacks[0].attack_bonus == 8


def test_2014_asis_and_hit_points_are_edition_specific() -> None:
    expected = {
        1: (16, 16, 13), 3: (16, 16, 31), 4: (18, 16, 40),
        6: (20, 16, 58), 7: (20, 16, 67), 8: (20, 18, 84),
        10: (20, 18, 104),
    }
    for level, (strength, constitution, hp) in expected.items():
        template = build_karnok_stoneward_2014_level(level)
        assert template.ability_scores is not None
        assert (template.ability_scores.strength, template.ability_scores.constitution, template.max_hp) == (
            strength, constitution, hp,
        )


def test_2014_indomitable_rerolls_without_2024_fighter_level_bonus() -> None:
    state = build_combatant_state(build_karnok_stoneward_2014_level(9))
    roll = use_indomitable(state, "wisdom", FixedDiceProvider([10]))

    assert roll is not None
    assert roll.selected_roll == 10
    assert roll.total == 10
    assert roll.notation.endswith("[Indomitable]")
    resource = next(item for item in state.resources if item.id == "indomitable")
    assert resource.current_uses == 0
