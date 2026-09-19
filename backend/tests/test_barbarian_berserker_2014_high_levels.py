from app.combat.barbarian import end_rage, end_rage_if_incapacitated, enter_rage, finish_rage_turn, rage_active
from app.combat.brutal_critical import brutal_critical_bonus_damage
from app.combat.damage_reaction_dispatch import plan_damage_reaction_attack, resolve_damage_reaction_attack
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.state import begin_turn, build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.barbarian_berserker_2014_profile import (
    _advancements, _base_scores, _compile_rokhan_stonefury_2014_profile,
    _final_scores, _species_increases,
)
from app.content.barbarian_berserker_2014_runtime import (
    _compile_rokhan_stonefury_2014, _damage_reaction, _progression, _scores,
    build_rokhan_stonefury_2014,
)
from app.content.demo import build_demo_fighter
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
    base = build_rokhan_stonefury_2014(13)
    features = base.progression_features.model_copy(update={"persistent_rage_2014": True})
    state = build_combatant_state(base.model_copy(update={"level": 15, "progression_features": features}))

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

    state = build_combatant_state(base.model_copy(update={"level": 15, "progression_features": features}))
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
    base = build_rokhan_stonefury_2014(13)
    features = base.progression_features.model_copy(update={
        "ability_check_minimums": [
            AbilityCheckMinimum(source_id="indomitable-might", ability="strength"),
        ],
    })
    state = build_combatant_state(base.model_copy(update={"level": 18, "progression_features": features}))
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



def test_staged_2014_level_20_unlimited_rage_has_no_counter_and_never_decrements() -> None:
    base = build_rokhan_stonefury_2014(13)
    features = base.progression_features.model_copy(update={"persistent_rage_2014": True})
    template = base.model_copy(update={
        "level": 20,
        "progression_features": features,
        "resources": [],
        "unlimited_resource_ids": ["rage"],
    })
    state = build_combatant_state(template)

    assert state.resources == []
    for round_number in (1, 2):
        begin_turn(state)
        event = enter_rage(round_number, round_number, state, "rokhan")
        assert event is not None
        assert event.resource_remaining is None
        assert state.resources == []
        assert end_rage(state) is not None



def _retaliation_setup(source_position: int = 5) -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    rokhan = EncounterCombatant(
        combatant_id="rokhan",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(_compile_rokhan_stonefury_2014(14)),
    )
    source = EncounterCombatant(
        combatant_id="source",
        side="monsters",
        position_ft=source_position,
        state=build_combatant_state(build_demo_fighter()),
    )
    return rokhan, source, EncounterSetup(
        heroes=[rokhan], monsters=[source], hero_total_levels=14, monster_total_cr="1", ruleset="2014",
    )


def test_staged_2014_level_14_retaliation_binds_universal_damage_reaction_policy() -> None:
    rule = _damage_reaction(14)

    assert rule is not None
    assert rule.source_feature == "retaliation"
    assert rule.trigger == "damaged-by-creature"
    assert rule.source_range_ft == 5
    assert rule.attack_kind == "melee"
    assert _damage_reaction(13) is None


def test_staged_2014_level_14_retaliation_plans_melee_attack_against_damage_source() -> None:
    rokhan, source, setup = _retaliation_setup()

    plan = plan_damage_reaction_attack(rokhan, source, setup, applied_damage=7)

    assert plan is not None
    assert plan.reactor.combatant_id == "rokhan"
    assert plan.source.combatant_id == "source"
    assert plan.attack.id == "rokhan-2014-greataxe"
    assert plan.distance_ft == 5


def test_staged_2014_level_14_retaliation_fails_closed_out_of_range_or_without_reaction() -> None:
    rokhan, source, setup = _retaliation_setup(source_position=10)
    assert plan_damage_reaction_attack(rokhan, source, setup, applied_damage=7) is None

    rokhan, source, setup = _retaliation_setup()
    rokhan.state.reaction_available = False
    assert plan_damage_reaction_attack(rokhan, source, setup, applied_damage=7) is None



def test_staged_2014_level_14_retaliation_resolves_off_turn_without_spending_action() -> None:
    rokhan, source, setup = _retaliation_setup()
    source_hp_before = source.state.current_hp
    action_before = rokhan.state.action_available

    event = resolve_damage_reaction_attack(
        5,
        2,
        rokhan,
        source,
        setup,
        applied_damage=7,
        dice=FixedDiceProvider([19, 6]),
        turn_key="2:source",
    )

    assert event is not None
    assert event.event_type == "attack"
    assert event.feature_id == "retaliation"
    assert event.actor_id == "rokhan"
    assert event.target_id == "source"
    assert source.state.current_hp < source_hp_before
    assert rokhan.state.reaction_available is False
    assert rokhan.state.action_available is action_before
    assert event.turn_terminated is False



def test_private_2014_candidate_compilers_cover_levels_14_through_20_without_public_exposure() -> None:
    for level in range(14, 21):
        template = _compile_rokhan_stonefury_2014(level)
        profile = _compile_rokhan_stonefury_2014_profile(level)

        assert template.level == profile.level == level
        assert template.id == profile.template_id
        assert template.ability_scores == profile.final_ability_scores
        assert template.damage_reaction_attack is not None
        assert template.damage_reaction_attack.source_feature == "retaliation"

    l20 = _compile_rokhan_stonefury_2014(20)
    assert (l20.ability_scores.strength, l20.ability_scores.constitution) == (24, 24)
    assert l20.resources == []
    assert l20.unlimited_resource_ids == ["rage"]

    for level in (14, 20):
        try:
            build_rokhan_stonefury_2014(level)
        except ValueError as exc:
            assert "certification covers levels 1 through 13" in str(exc)
        else:
            raise AssertionError("Uncertified high-level Rokhan must remain unavailable publicly.")
