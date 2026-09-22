from app.combat.cunning_action import needs_dash, use_dash
from app.combat.rogue_defenses import apply_uncanny_dodge, evasion_damage
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.rogue_thief_2014_profile import build_mara_quickstep_2014_profile
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DamageType


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(rogue: EncounterCombatant, target: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[rogue], monsters=[target], hero_total_levels=2, monster_total_cr="2", ruleset="2014",
    )


def test_2014_thief_levels_one_through_sixteen_are_isolated_from_2024() -> None:
    for level in range(1, 17):
        hero = build_mara_quickstep_2014(level)
        assert hero.ruleset == "2014"
        assert hero.level == level
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.progression_features.sneak_attack_d6 == (level + 1) // 2
        assert hero.source.startswith("D&D Basic Rules 2014")


def test_level_eleven_reliable_talent_is_audited_without_faking_roll_math() -> None:
    profile = build_mara_quickstep_2014_profile(11)
    reliable_talent = next(audit for audit in profile.feature_audits if audit.feature_id == "reliable-talent")
    assert reliable_talent.source_reference == "D&D Basic Rules 2014: Rogue"
    assert reliable_talent.combat_relevant is False
    assert reliable_talent.automated is False
    assert "no qualifying proficient ability check" in (reliable_talent.notes or "")

    hero = build_mara_quickstep_2014(11)
    assert hero.progression_features.sneak_attack_d6 == 6
    assert hero.ability_scores.dexterity == 20


def test_levels_twelve_and_thirteen_apply_approved_constitution_progression() -> None:
    profile12 = build_mara_quickstep_2014_profile(12)
    hero12 = build_mara_quickstep_2014(12)
    hero13 = build_mara_quickstep_2014(13)

    assert profile12.final_ability_scores.constitution == 16
    assert [(item.ability, item.amount) for item in profile12.advancement_increases if item.ability == "constitution"] == [
        ("constitution", 2),
    ]
    assert hero12.ability_scores.constitution == 16
    assert hero12.max_hp == 99
    assert hero12.saving_throw_bonuses["constitution"] == 3
    assert hero13.ability_scores.constitution == 16
    assert hero13.progression_features.sneak_attack_d6 == 7

    profile13 = build_mara_quickstep_2014_profile(13)
    use_magic_device = next(audit for audit in profile13.feature_audits if audit.feature_id == "use-magic-device")
    assert use_magic_device.combat_relevant is False
    assert use_magic_device.automated is False
    assert "arena-inert" in (use_magic_device.notes or "")


def test_levels_fourteen_through_sixteen_reuse_existing_engine_primitives() -> None:
    profile14 = build_mara_quickstep_2014_profile(14)
    blindsense = next(audit for audit in profile14.feature_audits if audit.feature_id == "blindsense")
    assert blindsense.combat_relevant is False
    assert blindsense.automated is False
    assert "location awareness within 10 feet" in (blindsense.notes or "")
    assert "no unresolved hidden-creature location loop" in (blindsense.notes or "")

    profile15 = build_mara_quickstep_2014_profile(15)
    slippery_mind = next(audit for audit in profile15.feature_audits if audit.feature_id == "slippery-mind")
    hero15 = build_mara_quickstep_2014(15)
    assert slippery_mind.combat_relevant is True
    assert slippery_mind.automated is True
    assert hero15.saving_throw_bonuses["wisdom"] == 7
    assert hero15.progression_features.sneak_attack_d6 == 8

    profile16 = build_mara_quickstep_2014_profile(16)
    hero16 = build_mara_quickstep_2014(16)
    assert profile16.final_ability_scores.constitution == 18
    assert [(item.ability, item.amount) for item in profile16.advancement_increases if item.ability == "constitution"] == [
        ("constitution", 2), ("constitution", 2),
    ]
    assert hero16.ability_scores.constitution == 18
    assert hero16.max_hp == 147
    assert hero16.saving_throw_bonuses["constitution"] == 4
    assert hero16.saving_throw_bonuses["wisdom"] == 7
    assert hero16.progression_features.sneak_attack_d6 == 8


def test_cunning_action_dash_is_used_only_when_it_enables_offense() -> None:
    rogue = _member(build_mara_quickstep_2014(2), "mara", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(2), "target", "monsters", 370)
    setup = _setup(rogue, target)
    rogue.state.movement_remaining_ft = 30
    assert needs_dash(rogue, setup, "1:mara") is True
    event = use_dash(1, 1, rogue, setup, "1:mara")
    assert event is not None and event.feature_id == "cunning-action-dash"
    assert rogue.state.movement_remaining_ft == 60
    assert rogue.state.bonus_action_available is False

    close = _member(build_mara_quickstep_2014(2), "close", "heroes", 0)
    close.state.movement_remaining_ft = 30
    near_target = _member(build_karnok_stoneward_2014(2), "near", "monsters", 100)
    near_setup = _setup(close, near_target)
    assert needs_dash(close, near_setup, "1:close") is False


def test_uncanny_dodge_requires_visible_attacker_and_spends_reaction() -> None:
    attacker = build_combatant_state(build_karnok_stoneward_2014(5))
    defender = build_combatant_state(build_mara_quickstep_2014(5))
    component = DamageRollComponent(
        source="test", notation="21", rolls=[21], modifier=0,
        damage_type=DamageType.SLASHING, total=21,
    )
    reduced, used = apply_uncanny_dodge(attacker, defender, [component])
    assert used is True
    assert reduced[0].total == 10
    assert defender.reaction_available is False

    hidden_attacker = build_combatant_state(build_karnok_stoneward_2014(5))
    hidden_attacker.active_effect_ids.append("invisible")
    fresh_defender = build_combatant_state(build_mara_quickstep_2014(5))
    unchanged, used = apply_uncanny_dodge(hidden_attacker, fresh_defender, [component])
    assert used is False
    assert unchanged[0].total == 21
    assert fresh_defender.reaction_available is True


def test_evasion_uses_2014_success_zero_failure_half_rule() -> None:
    rogue = build_combatant_state(build_mara_quickstep_2014(7))
    assert evasion_damage(rogue, "dexterity", True, "half", 21) == 0
    assert evasion_damage(rogue, "dexterity", False, "half", 21) == 10
    assert evasion_damage(rogue, "constitution", True, "half", 21) == 10
