from app.combat.deflect_missiles import apply_deflect_missiles
from app.combat.dice import FixedDiceProvider
from app.combat.monk_bonus_attacks_2014 import resolve_monk_bonus_attacks
from app.combat.open_hand_technique_2014 import resolve_open_hand_technique
from app.combat.rogue_defenses import evasion_damage
from app.combat.state import build_combatant_state
from app.combat.stunning_strike_2014 import resolve_stunning_strike
from app.content.certified_heroes import build_all_certified_hero_entries
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.models import DamageRollComponent, DamageType


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(monk: EncounterCombatant, target: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=monk.state.template.level or 1,
        monster_total_cr="5",
        ruleset="2014",
    )


def _qualifying_event(actor: EncounterCombatant) -> BattleEvent:
    return BattleEvent(
        sequence=1,
        round_number=1,
        event_type="attack",
        actor_id=actor.combatant_id,
        actor_name=actor.state.template.name,
        weapon_id="unarmed-strike",
        animation="strike",
        description="Qualifying Attack action hit.",
    )


def test_2014_open_hand_levels_one_through_ten_compile_with_expected_breakpoints() -> None:
    for level in range(1, 11):
        profile = build_kael_stillwater_2014_profile(level)
        combat = build_kael_2014_combat_profile(level)
        hero = build_kael_stillwater_2014(level)
        assert profile.ruleset == hero.ruleset == "2014"
        assert profile.final_ability_scores == hero.ability_scores == combat.abilities
        assert hero.weapon_masteries == []
        assert hero.weapon_attack.weapon.dice_size == (4 if level < 5 else 6)
        assert hero.speed_ft == (30 if level == 1 else 40 if level < 6 else 45 if level < 10 else 50)
        assert hero.progression_features.flurry_of_blows is (level >= 2)
        assert hero.progression_features.deflect_missiles is (level >= 3)
        assert hero.progression_features.open_hand_technique is (level >= 3)
        assert hero.progression_features.stunning_strike is (level >= 5)
        assert hero.progression_features.evasion is (level >= 7)
    assert build_kael_stillwater_2014(4).ability_scores.dexterity == 18
    assert build_kael_stillwater_2014(8).ability_scores.dexterity == 20


def test_monk_resources_healing_removal_and_purity_are_level_gated() -> None:
    level6 = build_kael_stillwater_2014(6)
    assert {item.id: item.max_uses for item in level6.resources} == {"ki": 6, "wholeness-of-body": 1}
    assert level6.healing_actions[0].healing_bonus == 18
    assert build_kael_stillwater_2014(7).condition_removal_actions[0].removable_conditions == ["charmed", "frightened"]
    assert build_kael_stillwater_2014(10).condition_immunities == ["poisoned"]


def test_deflect_missiles_reduces_ranged_weapon_damage_and_spends_reaction() -> None:
    monk = build_combatant_state(build_kael_stillwater_2014(3))
    fighter = build_karnok_stoneward_2014(3)
    ranged = next(attack for attack in [fighter.weapon_attack, *fighter.alternate_weapon_attacks]
                  if attack.weapon.attack_kind.value == "ranged")
    component = DamageRollComponent(
        source="shortbow",
        notation="1d6+3",
        rolls=[5],
        modifier=3,
        damage_type=DamageType.PIERCING,
        total=8,
    )
    reduced, used, reduction = apply_deflect_missiles(
        monk,
        ranged,
        [component],
        FixedDiceProvider([4]),
    )
    assert used is True
    assert reduction == 10
    assert reduced[0].total == 0
    assert monk.reaction_available is False


def test_stunning_strike_spends_ki_and_uses_shared_timed_condition_engine() -> None:
    monk = _member(build_kael_stillwater_2014(5), "kael", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(5), "target", "monsters", 5)
    event = resolve_stunning_strike(
        1,
        1,
        monk,
        target,
        monk.state.template.weapon_attack,
        FixedDiceProvider([1]),
        affected_states=[monk.state, target.state],
    )
    assert event is not None
    assert event.save_dc == 13
    assert event.save_succeeded is False
    assert event.resource_remaining == 4
    assert "stunned" in target.state.active_effect_ids
    assert target.state.timed_effects[0].expiry_timing == "source_turn_end"
    assert target.state.timed_effects[0].expires_round == 2


def test_open_hand_technique_uses_shared_save_and_prone_condition() -> None:
    monk = _member(build_kael_stillwater_2014(3), "kael", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(3), "target", "monsters", 5)
    event = resolve_open_hand_technique(1, 1, monk, target, FixedDiceProvider([1]))
    assert event is not None
    assert event.save_dc == 12
    assert event.save_succeeded is False
    assert "prone" in target.state.active_effect_ids


def test_flurry_consumes_one_ki_and_resolves_two_unarmed_bonus_attacks() -> None:
    monk = _member(build_kael_stillwater_2014(2), "kael", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(2), "target", "monsters", 5)
    setup = _setup(monk, target)
    events, sequence = resolve_monk_bonus_attacks(
        2,
        1,
        monk,
        setup,
        FixedDiceProvider([15, 2, 15, 2]),
        "1:kael",
        [_qualifying_event(monk)],
    )
    attacks = [event for event in events if event.event_type == "attack"]
    assert sequence == 4
    assert len(attacks) == 2
    assert all(event.feature_id == "flurry-of-blows" for event in attacks)
    assert monk.state.bonus_action_available is False
    assert next(item for item in monk.state.resources if item.id == "ki").current_uses == 1


def test_evasion_reuses_shared_rogue_primitive() -> None:
    monk = build_combatant_state(build_kael_stillwater_2014(7))
    assert evasion_damage(monk, "dexterity", True, "half", 21) == 0
    assert evasion_damage(monk, "dexterity", False, "half", 21) == 10


def test_2014_certified_catalog_reaches_sixty_hero_snapshots() -> None:
    entries = [entry for entry in build_all_certified_hero_entries() if entry[1].ruleset == "2014"]
    monks = [entry for entry in entries if entry[0][0] == "monk"]
    paladins = [entry for entry in entries if entry[0][0] == "paladin"]
    assert len(entries) == 60
    assert [entry[0][1] for entry in monks] == list(range(1, 11))
    assert [entry[0][1] for entry in paladins] == list(range(1, 11))
