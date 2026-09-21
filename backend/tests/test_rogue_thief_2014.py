from app.combat.attacks import resolve_attack
from app.combat.cunning_action import needs_dash, use_dash
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_initiative import roll_encounter_initiative, turn_order_for_round
from app.combat.rogue_defenses import apply_uncanny_dodge, evasion_damage
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.rogue_thief_2014_profile import build_mara_quickstep_2014_profile
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DamageType, RollMode


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(rogue: EncounterCombatant, target: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[rogue], monsters=[target], hero_total_levels=2, monster_total_cr="2", ruleset="2014",
    )


def test_2014_thief_levels_one_through_twenty_are_isolated_from_2024() -> None:
    for level in range(1, 21):
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


def test_levels_fourteen_through_sixteen_use_existing_state_without_fake_blindsense_sight() -> None:
    profile14 = build_mara_quickstep_2014_profile(14)
    blindsense = next(audit for audit in profile14.feature_audits if audit.feature_id == "blindsense")
    assert blindsense.combat_relevant is False
    assert blindsense.automated is False
    assert "does not grant sight" in (blindsense.notes or "")
    assert "no Hide/location-guess loop" in (blindsense.notes or "")

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


def test_level_seventeen_thiefs_reflexes_is_declarative_and_scales_sneak_attack() -> None:
    profile17 = build_mara_quickstep_2014_profile(17)
    reflexes = next(audit for audit in profile17.feature_audits if audit.feature_id == "thiefs-reflexes")
    hero17 = build_mara_quickstep_2014(17)

    assert reflexes.combat_relevant is True
    assert reflexes.automated is True
    assert hero17.progression_features.first_round_extra_turn_initiative_offset == -10
    assert hero17.progression_features.sneak_attack_d6 == 9


def test_thiefs_reflexes_schedules_second_round_one_turn_at_initiative_minus_ten() -> None:
    rogue = _member(build_mara_quickstep_2014(17), "mara", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(17), "target", "monsters", 5)
    setup = EncounterSetup(
        heroes=[rogue], monsters=[target], hero_total_levels=17, monster_total_cr="17", ruleset="2014",
    )
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([15, 12]))
    by_id = {member.combatant_id: member for member in [rogue, target]}

    assert initiative.turn_order == ["mara", "target"]
    assert turn_order_for_round(1, initiative, by_id) == ["mara", "target", "mara"]
    assert turn_order_for_round(2, initiative, by_id) == ["mara", "target"]


def test_level_eighteen_elusive_suppresses_only_advantage_while_not_incapacitated() -> None:
    profile18 = build_mara_quickstep_2014_profile(18)
    elusive = next(audit for audit in profile18.feature_audits if audit.feature_id == "elusive")
    hero18 = build_mara_quickstep_2014(18)

    assert elusive.combat_relevant is True
    assert elusive.automated is True
    assert hero18.progression_features.suppress_attack_advantage_while_not_incapacitated is True
    assert hero18.progression_features.sneak_attack_d6 == 9

    attacker = build_combatant_state(build_karnok_stoneward_2014(18))
    defender = build_combatant_state(hero18)
    normal = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([3]), spend_action=False, advantage_sources=1,
    )
    assert normal.attack_roll.mode is RollMode.NORMAL

    attacker2 = build_combatant_state(build_karnok_stoneward_2014(18))
    defender2 = build_combatant_state(hero18)
    defender2.active_effect_ids.append("stunned")
    advantaged = resolve_attack(
        2, 1, attacker2, defender2, attacker2.template.weapon_attack, 5,
        FixedDiceProvider([3, 17, 4, 4]), spend_action=False, advantage_sources=1,
    )
    assert advantaged.attack_roll.mode is RollMode.ADVANTAGE


def test_level_nineteen_applies_final_constitution_asi_and_sneak_attack_ten_d6() -> None:
    profile19 = build_mara_quickstep_2014_profile(19)
    hero19 = build_mara_quickstep_2014(19)
    asi = next(audit for audit in profile19.feature_audits if audit.feature_id == "ability-score-improvement-l19")

    assert asi.combat_relevant is True
    assert asi.automated is True
    assert profile19.final_ability_scores.constitution == 20
    assert hero19.ability_scores.constitution == 20
    assert hero19.max_hp == 193
    assert hero19.saving_throw_bonuses["constitution"] == 5
    assert hero19.saving_throw_bonuses["wisdom"] == 8
    assert hero19.progression_features.sneak_attack_d6 == 10


def test_level_twenty_stroke_of_luck_overrides_natural_one_and_spends_resource() -> None:
    profile20 = build_mara_quickstep_2014_profile(20)
    stroke = next(audit for audit in profile20.feature_audits if audit.feature_id == "stroke-of-luck")
    hero20 = build_mara_quickstep_2014(20)

    assert stroke.combat_relevant is True
    assert stroke.automated is True
    assert hero20.progression_features.miss_to_hit_override_resource_id == "stroke-of-luck"
    assert {item.id: item.max_uses for item in hero20.resources} == {"stroke-of-luck": 1}
    assert hero20.progression_features.sneak_attack_d6 == 10

    attacker = build_combatant_state(hero20)
    defender = build_combatant_state(build_karnok_stoneward_2014(20))
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([1, 4]), spend_action=False,
    )

    assert event.attack_roll.selected_roll == 1
    assert event.hit is True
    assert event.critical is False
    assert event.turn_terminated is False
    assert event.turn_termination_reason is None
    assert event.feature_id == "stroke-of-luck"
    assert "Stroke Of Luck turns the miss into a hit." in event.description
    assert next(item for item in attacker.resources if item.id == "stroke-of-luck").current_uses == 0

    second = resolve_attack(
        2, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([1]), spend_action=False,
    )
    assert second.hit is False
    assert second.turn_terminated is True
    assert second.turn_termination_reason == "iron-pit-natural-1-attack"
