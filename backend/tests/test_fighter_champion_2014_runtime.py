from app.combat.dice import FixedDiceProvider
from app.combat.indomitable import use_indomitable
from app.combat.state import begin_turn, build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014


def _resource_uses(hero, resource_id: str) -> int:
    return next(item.max_uses for item in hero.resources if item.id == resource_id)


def test_2014_champion_levels_one_through_twenty_stay_in_2014_rules() -> None:
    for level in range(1, 21):
        hero = build_karnok_stoneward_2014(level)
        assert hero.ruleset == "2014"
        assert hero.level == level
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.source.startswith("D&D Basic Rules 2014")


def test_2014_champion_progression_uses_real_fighter_breakpoints() -> None:
    l1 = build_karnok_stoneward_2014(1); l5 = build_karnok_stoneward_2014(5)
    l10 = build_karnok_stoneward_2014(10); l11 = build_karnok_stoneward_2014(11)
    l13 = build_karnok_stoneward_2014(13); l15 = build_karnok_stoneward_2014(15)
    l17 = build_karnok_stoneward_2014(17); l18 = build_karnok_stoneward_2014(18)
    l20 = build_karnok_stoneward_2014(20)

    assert l1.progression_features.critical_hit_minimum == 20
    assert build_karnok_stoneward_2014(3).progression_features.critical_hit_minimum == 19
    assert l15.progression_features.critical_hit_minimum == 18
    assert len(l1.attack_action.slots) == 1
    assert len(l5.attack_action.slots) == 2
    assert len(l11.attack_action.slots) == 3
    assert len(l20.attack_action.slots) == 4
    assert "Archery" in l10.fighting_styles
    assert _resource_uses(l13, "indomitable") == 2
    assert _resource_uses(l17, "indomitable") == 3
    assert _resource_uses(l17, "action-surge") == 2
    assert l18.progression_features.survivor_heal_amount == 9
    assert l20.progression_features.survivor_heal_amount == 10


def test_2014_high_level_ability_scores_follow_declared_asi_choices() -> None:
    l12 = build_karnok_stoneward_2014(12).ability_scores
    l14 = build_karnok_stoneward_2014(14).ability_scores
    l16 = build_karnok_stoneward_2014(16).ability_scores
    l19 = build_karnok_stoneward_2014(19).ability_scores

    assert (l12.dexterity, l12.constitution, l12.wisdom) == (15, 18, 13)
    assert (l14.dexterity, l14.constitution, l14.wisdom) == (16, 19, 13)
    assert (l16.dexterity, l16.constitution, l16.wisdom) == (18, 19, 13)
    assert (l19.dexterity, l19.constitution, l19.wisdom) == (18, 20, 14)


def test_2014_survivor_heals_only_when_alive_at_or_below_half_hp() -> None:
    state = build_combatant_state(build_karnok_stoneward_2014(18))
    state.current_hp = state.template.max_hp // 2
    before = state.current_hp
    begin_turn(state)
    assert state.current_hp == min(state.template.max_hp, before + 9)

    state.current_hp = state.template.max_hp // 2 + 1
    before = state.current_hp
    begin_turn(state)
    assert state.current_hp == before

    state.current_hp = 0
    begin_turn(state)
    assert state.current_hp == 0


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


def test_2014_champion_has_no_2024_only_progression_features() -> None:
    progression = build_karnok_stoneward_2014(20).progression_features
    assert progression.initiative_advantage is False
    assert progression.athletics_advantage is False
    assert progression.heroic_warrior is False
    assert progression.tactical_master_sap_weapon_ids == []
    assert progression.tactical_shift_fraction == 0.0
    assert progression.critical_move_fraction == 0.0
