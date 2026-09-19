from app.combat.barbarian import end_rage_if_incapacitated, enter_rage, finish_rage_turn, rage_active
from app.combat.brutal_critical import brutal_critical_bonus_damage
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
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
