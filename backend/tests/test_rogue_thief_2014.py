from app.combat.cunning_action import needs_dash, use_dash
from app.combat.rogue_defenses import apply_uncanny_dodge, evasion_damage
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
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


def test_2014_thief_levels_one_through_ten_are_isolated_from_2024() -> None:
    for level in range(1, 11):
        hero = build_mara_quickstep_2014(level)
        assert hero.ruleset == "2014"
        assert hero.level == level
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.mastery_property is None
        assert all(attack.weapon.mastery_property is None for attack in hero.alternate_weapon_attacks)
        assert hero.progression_features.sneak_attack_d6 == (level + 1) // 2
        assert hero.source.startswith("D&D Basic Rules 2014")


def test_cunning_action_dash_is_used_only_when_it_enables_offense() -> None:
    rogue = _member(build_mara_quickstep_2014(2), "mara", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(2), "target", "monsters", 130)
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
