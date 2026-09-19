from app.combat.barbarian import end_rage, end_rage_if_incapacitated, enter_rage, finish_rage_turn, rage_active
from app.combat.brutal_critical import brutal_critical_bonus_damage
from app.combat.damage_reaction_dispatch import resolve_damage_event_reactions
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.state import begin_turn, build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.barbarian_berserker_2014_profile import (
    _advancements, _base_scores, _final_scores, _species_increases,
)
from app.content.barbarian_berserker_2014_runtime import (
    _progression, _scores, build_rokhan_stonefury_2014,
)
from app.content.demo import build_goblin_warrior
from app.content.level_resources import barbarian_2014_rage_uses, barbarian_rage_damage_bonus
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.progression import AbilityCheckMinimum


def test_2014_level_11_relentless_rage_reuses_effect_bound_survival_save() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(11))
    rule = state.template.progression_features.effect_bound_survival_save
    assert rule is not None
    assert rule.model_dump() == {
        "source_id": "relentless-rage",
        "required_effect_id": "rage",
        "save_ability": "constitution",
        "initial_dc": 10,
        "dc_increment": 5,
        "replacement_hp": 1,
    }

    assert enter_rage(1, 1, state, "rokhan") is not None
    state.current_hp = 1
    assert apply_damage(state, 1, dice=FixedDiceProvider([4])) == "survival_save"
    assert state.current_hp == 1
    assert state.survival_save_uses == {"relentless-rage": 1}


def test_2014_level_12_asi_updates_all_derived_combat_values() -> None:
    hero = build_rokhan_stonefury_2014(12)
    assert (
        hero.ability_scores.strength,
        hero.ability_scores.constitution,
        hero.ability_scores.wisdom,
    ) == (20, 16, 14)
    assert (hero.armor_class, hero.max_hp, hero.speed_ft) == (15, 125, 40)
    assert (hero.weapon_attack.attack_bonus, hero.weapon_attack.damage_bonus) == (9, 5)
    assert hero.saving_throw_bonuses["constitution"] == 7
    assert hero.saving_throw_bonuses["wisdom"] == 2
    assert hero.rage_damage_bonus == 3
    assert {item.id: item.max_uses for item in hero.resources} == {"rage": 5}


def test_2014_level_15_persistent_rage_uses_full_duration_without_maintenance() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(15))

    assert enter_rage(1, 1, state, "rokhan") is not None
    assert state.rage_expires_round == 11
    assert state.rage_max_round == 11
    assert finish_rage_turn(state, 2) is None
    assert rage_active(state) is True
    state.active_effect_ids.append("stunned")
    end_rage_if_incapacitated(state)
    assert rage_active(state) is True
    state.is_unconscious = True
    end_rage_if_incapacitated(state)
    assert rage_active(state) is False

    state = build_combatant_state(build_rokhan_stonefury_2014(15))
    assert enter_rage(2, 1, state, "rokhan") is not None
    assert finish_rage_turn(state, 11) == 1
    assert rage_active(state) is False


def test_2014_level_13_brutal_critical_adds_two_weapon_dice() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(13))
    attack = state.template.weapon_attack
    bonus = brutal_critical_bonus_damage(state, attack, True)
    assert bonus is not None
    source, count, sides, damage_type = bonus
    assert (source, count, sides) == ("Brutal Critical", 2, 12)
    assert damage_type == attack.weapon.damage_type
    assert attack.attack_bonus == 10
    assert state.template.max_hp == 135



def test_2014_level_18_indomitable_might_uses_auditable_strength_check_floor() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(18))
    apply_grapple(state, "monster-1", 19, 5, restrains=True)
    event = resolve_escape_grapple(1, 1, "rokhan", state, FixedDiceProvider([1]))
    assert event.check_succeeded is True
    assert event.ability_check_roll is not None
    assert event.ability_check_roll.total == 20
    revision = event.ability_check_roll.revisions[-1]
    assert revision.source_effect_id == "indomitable-might"
    assert revision.kind == "total_replacement"
    assert (revision.original_total, revision.replacement_total) == (11, 20)
    assert revision.accepted == "replacement"



def test_staged_2014_levels_15_through_19_have_exact_numeric_deltas() -> None:
    l15 = _progression(15, _scores(15))
    l16 = _scores(16)
    l17 = _progression(17, _scores(17))
    l19 = _scores(19)

    assert l15.persistent_rage_2014 is True
    assert (l16.strength, l16.constitution, barbarian_rage_damage_bonus(16)) == (20, 18, 4)
    assert l17.brutal_critical_dice == 3
    assert barbarian_2014_rage_uses(17) == 6
    assert (l19.strength, l19.constitution) == (20, 20)


def test_staged_2014_level_20_primal_champion_scores_are_24_but_rage_fails_closed() -> None:
    runtime_scores = _scores(20)
    profile_scores = _final_scores(_base_scores(), _species_increases(), _advancements(20))

    assert (runtime_scores.strength, runtime_scores.constitution) == (24, 24)
    assert profile_scores == runtime_scores
    try:
        barbarian_2014_rage_uses(20)
    except ValueError as exc:
        assert "Unlimited" in str(exc)
    else:
        raise AssertionError("2014 level-20 Rage must remain fail-closed until unlimited resources exist.")



def test_2014_level_20_unlimited_rage_has_no_counter_and_never_decrements() -> None:
    state = build_combatant_state(build_rokhan_stonefury_2014(20))

    assert state.resources == []
    for round_number in (1, 2):
        begin_turn(state)
        event = enter_rage(round_number, round_number, state, "rokhan")
        assert event is not None
        assert event.resource_remaining is None
        assert state.resources == []
        assert end_rage(state) is not None



def test_2014_level_14_retaliation_attacks_damage_source_and_spends_only_reaction() -> None:
    rokhan = EncounterCombatant(
        combatant_id="rokhan",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_rokhan_stonefury_2014(14)),
    )
    goblin = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[rokhan],
        monsters=[goblin],
        hero_total_levels=14,
        monster_total_cr="1/4",
    )
    triggering = resolve_encounter_attack(
        1, 1, goblin, rokhan, goblin.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 4]), setup, spend_action=False,
    )
    action_before = rokhan.state.action_available
    reactions, sequence = resolve_damage_event_reactions(
        2, 1, goblin, triggering, setup, FixedDiceProvider([19, 5]),
        turn_key="1:goblin",
    )

    assert [event.feature_id for event in reactions] == ["retaliation"]
    assert reactions[0].actor_id == "rokhan"
    assert reactions[0].target_id == "goblin"
    assert reactions[0].weapon_id == "greataxe"
    assert rokhan.state.reaction_available is False
    assert rokhan.state.action_available is action_before
    assert sequence == 3


def test_2014_levels_14_through_20_are_real_runnable_templates() -> None:
    heroes = [build_rokhan_stonefury_2014(level) for level in range(14, 21)]

    assert all(hero.ruleset == "2014" for hero in heroes)
    assert heroes[0].damage_triggered_melee_reaction is not None
    assert heroes[0].damage_triggered_melee_reaction.id == "retaliation"
    assert heroes[1].progression_features.persistent_rage_2014 is True
    assert heroes[3].progression_features.brutal_critical_dice == 3
    assert heroes[4].progression_features.ability_check_minimums[0].source_id == "indomitable-might"
    assert (heroes[-1].ability_scores.strength, heroes[-1].ability_scores.constitution) == (24, 24)
    assert heroes[-1].unlimited_resource_ids == ["rage"]
