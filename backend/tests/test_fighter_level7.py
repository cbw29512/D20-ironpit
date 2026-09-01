from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_champion_progression_profile import build_karnok_stoneward_level7_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_karnok_stoneward_level7_combat_profile
from app.domain.models import RollMode


def test_fighter_level_seven_snapshot_adds_great_weapon_fighting_only_to_greatsword() -> None:
    karnok = build_karnok_stoneward_level(7)
    greatsword = karnok.weapon_attack
    shortbow = karnok.alternate_weapon_attacks[0]

    assert (karnok.id, karnok.level, karnok.max_hp, karnok.armor_class, karnok.speed_ft) == (
        "karnok-stoneward-l7", 7, 67, 17, 30,
    )
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (8, 5, 3)
    assert (shortbow.attack_bonus, shortbow.damage_bonus, shortbow.damage_die_minimum) == (4, 1, None)
    assert karnok.progression_features.great_weapon_fighting is True
    assert karnok.progression_features.critical_hit_minimum == 19
    assert karnok.progression_features.tactical_shift_fraction == 0.5
    assert karnok.attack_action is not None and len(karnok.attack_action.slots) == 2


def test_great_weapon_fighting_treats_each_one_or_two_as_three_and_scales_on_critical() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(7))
    attack = state.template.weapon_attack

    normal, normal_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([1, 2]), False, RollMode.NORMAL, None,
    )
    critical, critical_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([1, 2, 1, 2]), True, RollMode.NORMAL, None,
    )

    assert normal.total == 11 and normal_components[0].rolls == [3, 3]
    assert critical.total == 17 and critical_components[0].rolls == [3, 3, 3, 3]


def test_great_weapon_fighting_does_not_change_shortbow_damage() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(7))
    shortbow = state.template.alternate_weapon_attacks[0]
    total, components = resolve_weapon_damage(
        state, shortbow, FixedDiceProvider([1]), False, RollMode.NORMAL, None,
    )
    assert total.total == 2
    assert components[0].rolls == [1]


def test_savage_attacker_compares_great_weapon_fighting_adjusted_weapon_rolls() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(7))
    total, components = resolve_weapon_damage(
        state, state.template.weapon_attack, FixedDiceProvider([1, 2, 1, 6]),
        False, RollMode.NORMAL, "turn-1:karnok",
    )
    assert total.total == 14
    assert components[0].rolls == [3, 6]
    assert components[0].source == "Greatsword (Savage Attacker)"


def test_fighter_level_seven_profile_fingerprint_resources_and_registry_pass_all_gates() -> None:
    template = build_karnok_stoneward_level(7)
    profile = build_karnok_stoneward_level7_profile()
    combat_profile = build_karnok_stoneward_level7_combat_profile()

    assert profile.final_ability_scores.strength == 20
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("strength", 1), ("constitution", 1), ("strength", 2),
    ]
    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)
    assert_character_resources_raw_ready(template, profile, combat_profile)
    assert build_certified_hero_registry()[("fighter", 7, "canonical")] == (
        "Karnok Stoneward", "karnok-stoneward-l7",
    )
