from app.combat.dice import FixedDiceProvider
from app.combat.indomitable import use_indomitable
from app.combat.state import build_combatant_state
from app.content.build_audit import audit_character_build
from app.content.certified_heroes_2014 import build_certified_hero_entries_2014
from app.content.character_resource_audit import audit_character_resources
from app.content.fighter_2014 import build_karnok_stoneward_2014
from app.content.fighter_2014_combat_profile import build_karnok_stoneward_2014_combat_profile
from app.content.fighter_2014_profile import build_karnok_stoneward_2014_profile
from app.content.pregen_combat_audit import audit_pregen_combat_stats


def test_2014_karnok_levels_one_through_ten_pass_every_certification_gate() -> None:
    entries = build_certified_hero_entries_2014()

    assert len(entries) == 10
    assert [template.level for _, template in entries] == list(range(1, 11))
    for key, template in entries:
        profile = build_karnok_stoneward_2014_profile(template.level)
        fingerprint = build_karnok_stoneward_2014_combat_profile(template.level)
        assert key == ("2014", "fighter", template.level, "canonical-2014")
        assert template.ruleset == "2014"
        assert audit_character_build(profile, template) == []
        assert audit_pregen_combat_stats(template, fingerprint) == []
        assert audit_character_resources(template, profile, fingerprint) == []
        assert template.weapon_masteries == []
        assert template.wearing_heavy_armor is True
        assert all(attack.weapon.mastery_property is None for attack in [
            template.weapon_attack, *template.alternate_weapon_attacks,
        ])


def test_2014_champion_progression_keeps_edition_specific_breakpoints() -> None:
    level_1 = build_karnok_stoneward_2014(1)
    level_3 = build_karnok_stoneward_2014(3)
    level_5 = build_karnok_stoneward_2014(5)
    level_7 = build_karnok_stoneward_2014(7)
    level_10 = build_karnok_stoneward_2014(10)

    assert {item.id: item.max_uses for item in level_1.resources} == {"second-wind": 1}
    assert level_3.progression_features.critical_hit_minimum == 19
    assert level_5.attack_action is not None and len(level_5.attack_action.slots) == 2
    assert level_7.initiative_bonus == 4
    assert level_10.fighting_styles == ["Defense", "Archery"]
    assert level_10.alternate_weapon_attacks[0].weapon.id == "longbow"
    assert level_10.alternate_weapon_attacks[0].attack_bonus == 8


def test_2014_indomitable_rerolls_without_the_2024_fighter_level_bonus() -> None:
    state = build_combatant_state(build_karnok_stoneward_2014(9))
    resource = next(item for item in state.resources if item.id == "indomitable")

    roll = use_indomitable(state, "wisdom", FixedDiceProvider([10]))

    assert roll is not None
    assert roll.selected_roll == 10
    assert roll.total == 10
    assert roll.notation.endswith("[Indomitable]")
    assert resource.current_uses == 0


def test_2014_profile_uses_human_six_score_increase_and_never_weapon_mastery() -> None:
    profile = build_karnok_stoneward_2014_profile(10)

    assert len(profile.species_increases) == 6
    assert profile.background_increases == []
    assert profile.origin_feat_id is None
    assert profile.weapon_masteries == []
    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.constitution == 18
