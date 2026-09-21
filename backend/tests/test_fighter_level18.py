from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.fighter_endgame_profile import build_karnok_stoneward_level18_profile
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.models import RollMode


def test_fighter_eighteen_is_level_seventeen_plus_survivor_delta() -> None:
    level17 = build_karnok_stoneward_level(17)
    level18 = build_karnok_stoneward_level(18)
    profile = build_karnok_stoneward_level18_profile()
    combat = build_pregen_combat_profiles()[level18.id]

    assert level18.max_hp == level17.max_hp + 11 == 202
    assert level18.ability_scores == level17.ability_scores
    assert level18.progression_features.death_save_advantage is True
    assert level18.progression_features.death_save_recovery_minimum == 18
    assert level18.progression_features.bloodied_start_turn_heal_amount == 10
    assert next(item for item in profile.feature_audits if item.feature_id == "survivor").automated is True

    assert_canonical_profile_policy(profile)
    assert audit_character_build(profile, level18) == []
    assert_character_build_raw_ready(profile, level18)
    assert audit_pregen_combat_stats(level18, combat) == []
    assert_pregen_combat_stats(level18, combat)
    assert_character_resources_raw_ready(level18, profile, combat)


def test_survivor_heroic_rally_reuses_bloodied_start_turn_healing() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(18))
    state.current_hp = 101
    begin_turn(state)
    assert state.current_hp == 111

    state.current_hp = 102
    begin_turn(state)
    assert state.current_hp == 102


def test_survivor_defy_death_reuses_universal_death_save_rules() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(18))
    assert apply_damage(state, state.current_hp) == "unconscious"

    event = resolve_death_save(1, 1, "karnok18", state, FixedDiceProvider([5, 18]))
    assert event.death_save_roll is not None
    assert event.death_save_roll.mode is RollMode.ADVANTAGE
    assert event.death_save_roll.selected_roll == 18
    assert state.current_hp == 1
    assert state.is_unconscious is False
    assert state.death_save_successes == 0
    assert state.death_save_failures == 0
