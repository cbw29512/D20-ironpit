from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.combat.tactical_shift import resolve_tactical_shift
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.demo import build_goblin_warrior
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import build_karnok_stoneward_level5_profile
from app.content.pregen_combat_audit import assert_pregen_combat_stats, audit_pregen_combat_stats
from app.content.pregen_combat_profiles import build_karnok_stoneward_level5_combat_profile
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup(distance: int = 5) -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:karnok-l5", side="heroes", position_ft=0,
        state=build_combatant_state(build_karnok_stoneward_level(5)),
    )
    target_template = build_goblin_warrior().model_copy(update={"max_hp": 200})
    monster = EncounterCombatant(
        combatant_id="monster-1:training-target", side="monsters", position_ft=distance,
        state=build_combatant_state(target_template),
    )
    setup = EncounterSetup(heroes=[hero], monsters=[monster], hero_total_levels=5, monster_total_cr="1/4")
    return hero, monster, setup


def test_fighter_level_five_snapshot_scales_pb_hp_resources_and_extra_attack() -> None:
    karnok = build_karnok_stoneward_level(5)
    resources = {resource.id: resource.max_uses for resource in karnok.resources}
    attacks = {attack.id: attack for attack in [karnok.weapon_attack, *karnok.alternate_weapon_attacks]}

    assert (karnok.id, karnok.level, karnok.max_hp) == ("karnok-stoneward-l5", 5, 49)
    assert (attacks["karnok-greatsword"].attack_bonus, attacks["karnok-greatsword"].damage_bonus) == (7, 4)
    assert (attacks["karnok-shortbow"].attack_bonus, attacks["karnok-shortbow"].damage_bonus) == (4, 1)
    assert karnok.saving_throw_bonuses["strength"] == 7
    assert karnok.saving_throw_bonuses["constitution"] == 6
    assert karnok.skill_bonuses["athletics"] == 7
    assert resources == {"second-wind": 3, "action-surge": 1, "adrenaline-rush": 3, "relentless-endurance": 1}
    assert karnok.progression_features.tactical_shift_fraction == 0.5
    assert karnok.attack_action is not None
    assert len(karnok.attack_action.slots) == 2
    assert all(slot.attack_ids == ["karnok-greatsword", "karnok-shortbow"] for slot in karnok.attack_action.slots)


def test_fighter_level_five_profile_and_candidate_fingerprint_pass_audits() -> None:
    template = build_karnok_stoneward_level(5)
    profile = build_karnok_stoneward_level5_profile()
    combat_profile = build_karnok_stoneward_level5_combat_profile()

    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert audit_pregen_combat_stats(template, combat_profile) == []
    assert_pregen_combat_stats(template, combat_profile)


def test_tactical_shift_moves_half_speed_without_spending_normal_movement() -> None:
    hero, monster, setup = _setup(distance=35)
    hero.state.movement_remaining_ft = 30

    event = resolve_tactical_shift(1, 1, hero, setup)

    assert event is not None
    assert event.feature_id == "tactical-shift"
    assert event.movement_ft == 15
    assert (event.distance_before_ft, event.distance_after_ft) == (35, 20)
    assert hero.position_ft == 15
    assert hero.state.movement_remaining_ft == 30
    assert monster.state.reaction_available is True


def test_tactical_shift_cannot_move_when_fighter_speed_is_zero() -> None:
    hero, monster, setup = _setup(distance=35)
    apply_grapple(hero.state, monster.combatant_id, escape_dc=12, range_ft=40)

    event = resolve_tactical_shift(1, 1, hero, setup)

    assert event is None
    assert hero.position_ft == 0
    assert monster.state.reaction_available is True


def test_extra_attack_and_action_surge_each_resolve_two_attacks() -> None:
    hero, _, setup = _setup(distance=5)
    # Four deliberate misses prove each Attack action resolves two attack rolls
    # without coupling this regression to Savage Attacker's damage rerolls.
    dice = FixedDiceProvider([2, 2, 2, 2])

    first_events, sequence = resolve_attack_action(1, 1, hero, setup, dice)
    surge_events, _ = resolve_action_surge_attack(sequence, 1, hero, setup, dice, "1:hero-1:karnok-l5")

    assert len([event for event in first_events if event.event_type == "attack"]) == 2
    assert len([event for event in surge_events if event.event_type == "attack"]) == 2
    assert any(event.feature_id == "action-surge" for event in surge_events)
