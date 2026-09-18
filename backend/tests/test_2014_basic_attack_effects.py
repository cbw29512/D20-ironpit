from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_attack_effects_2014 import supports_basic_attack_effects_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait


_ATTACK_EFFECT_IDS = {
    "constrictor-snake", "crocodile", "flying-snake", "giant-constrictor-snake",
    "giant-crab", "roc", "tyrannosaurus-rex",
}
_SAVE_PRONE_IDS = {
    "ankylosaurus", "dire-wolf", "giant-crocodile", "mastiff", "wolf", "worg",
}
_SAVE_DAMAGE_IDS = {
    "giant-centipede", "giant-poisonous-snake", "giant-scorpion", "giant-wasp",
    "poisonous-snake", "scorpion", "wyvern",
}
_CHARGE_IDS = {
    "allosaurus", "elephant", "elk", "giant-elk", "giant-sea-horse", "mammoth",
    "minotaur-skeleton", "panther", "rhinoceros", "saber-toothed-tiger", "tiger",
    "triceratops", "warhorse",
}
_SURE_FOOTED_IDS = {"goat", "giant-goat", "mule"}
_SWARM_IDS = {"swarm-of-insects", "swarm-of-poisonous-snakes", "swarm-of-rats", "swarm-of-ravens"}


def _attack_id(monster_id: str, attack_id: str) -> str:
    return f"2014-{monster_id}-{attack_id}".replace("--", "-")


def _runtime_attacks(template):
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return {attack.id: attack for attack in attacks}


def _enum_value(value):
    return value.value if hasattr(value, "value") else value


def test_basic_attack_effect_tranche_is_exactly_101_and_ruleset_isolated():
    source = load_monster_source_2014()
    ready = [monster for monster in source if not basic_blockers_2014(monster)]
    assert len(ready) == 101
    expected = (
        _ATTACK_EFFECT_IDS | _SAVE_PRONE_IDS | _SAVE_DAMAGE_IDS | _CHARGE_IDS |
        _SURE_FOOTED_IDS | _SWARM_IDS
    )
    assert expected <= {monster.id for monster in ready}
    for monster in ready:
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.ruleset == "2014"
        assert template.id == f"2014-{monster.id}"


def test_basic_attack_effects_preserve_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _ATTACK_EFFECT_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        for source_attack in monster.attacks:
            runtime = runtime_attacks[_attack_id(monster.id, source_attack.id)]
            assert len(runtime.on_hit_damage) == len(source_attack.on_hit_damage)
            for expected, actual in zip(source_attack.on_hit_damage, runtime.on_hit_damage, strict=True):
                assert actual.source == source_attack.name
                assert actual.dice_count == expected["dice_count"]
                assert actual.dice_size == expected["dice_size"]
                assert actual.damage_bonus == expected.get("bonus", 0)
                assert _enum_value(actual.damage_type) == str(expected["type"]).lower()
            expected_control = source_attack.control_effect
            if expected_control is None:
                assert runtime.control_effect is None
            else:
                assert runtime.control_effect is not None
                assert runtime.control_effect.grapple_escape_dc == expected_control["grapple_escape_dc"]
                assert runtime.control_effect.restrains_while_grappled == expected_control.get("restrains_while_grappled", False)
            assert runtime.forbid_target_grappled_by_self == source_attack.forbid_target_grappled_by_self


def test_save_to_prone_riders_preserve_exact_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _SAVE_PRONE_IDS:
        monster = source[monster_id]
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        for source_attack in [attack for attack in monster.attacks if attack.on_hit_save_effect is not None]:
            expected = source_attack.on_hit_save_effect
            runtime = runtime_attacks[_attack_id(monster.id, source_attack.id)].on_hit_condition_save
            assert expected is not None and runtime is not None
            assert _enum_value(runtime.save_ability) == str(expected["save_ability"]).lower()
            assert runtime.dc == expected["dc"]
            assert runtime.condition_id == "prone"


def test_save_damage_riders_preserve_exact_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _SAVE_DAMAGE_IDS:
        monster = source[monster_id]
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        for source_attack in [attack for attack in monster.attacks if attack.on_hit_save_effect is not None]:
            expected = source_attack.on_hit_save_effect
            runtime = runtime_attacks[_attack_id(monster.id, source_attack.id)].on_hit_save_damage
            assert expected is not None and runtime is not None
            assert runtime.source == source_attack.name
            assert _enum_value(runtime.save_ability) == str(expected["save_ability"]).lower()
            assert runtime.dc == expected["dc"]
            assert runtime.dice_count == expected["damage_dice_count"]
            assert runtime.dice_size == expected["damage_dice_size"]
            assert runtime.damage_bonus == expected.get("damage_bonus", 0)
            assert _enum_value(runtime.damage_type) == str(expected["damage_type"]).lower()
            assert runtime.success_damage == expected["success_damage"]


def test_charge_profiles_preserve_exact_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _CHARGE_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        charge_attacks = [attack for attack in monster.attacks if attack.charge_profile is not None]
        assert charge_attacks
        for source_attack in charge_attacks:
            expected = corrected_charge_profile_2014(monster, source_attack)
            actual = runtime_attacks[_attack_id(monster.id, source_attack.id)].charge_profile
            assert isinstance(expected, dict) and actual is not None
            assert actual.minimum_move_ft == expected["minimum_move_ft"]
            bonus = expected.get("bonus_damage")
            if bonus is None:
                assert actual.bonus_damage is None
            else:
                assert actual.bonus_damage is not None
                assert actual.bonus_damage.dice_count == bonus["dice_count"]
                assert actual.bonus_damage.dice_size == bonus["dice_size"]
                assert actual.bonus_damage.damage_bonus == bonus["damage_bonus"]
                assert _enum_value(actual.bonus_damage.damage_type) == bonus["damage_type"]
            ability = expected.get("prone_save_ability")
            assert (_enum_value(actual.prone_save_ability) if actual.prone_save_ability else None) == ability
            assert actual.prone_save_dc == expected.get("prone_save_dc")
            follow_up = expected.get("follow_up_attack_id")
            expected_runtime_id = _attack_id(monster.id, follow_up) if follow_up else None
            assert actual.follow_up_attack_id == expected_runtime_id
            assert actual.follow_up_required_target_condition == ("prone" if follow_up else None)
            assert actual.follow_up_action_cost == ("bonus_action" if follow_up else "free")


def test_swarm_conditional_damage_uses_shared_runtime_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _SWARM_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert CombatTrait.SWARM in template.combat_traits
        runtime_attacks = _runtime_attacks(template)
        for source_attack in monster.attacks:
            expected_rows = source_attack.conditional_damage
            actual_rows = runtime_attacks[_attack_id(monster.id, source_attack.id)].conditional_damage
            assert len(actual_rows) == len(expected_rows)
            for expected, actual in zip(expected_rows, actual_rows, strict=True):
                assert actual.trigger == expected["trigger"]
                assert actual.mode == expected["mode"]
                assert actual.dice_count == expected["dice_count"]
                assert actual.dice_size == expected["dice_size"]
                assert actual.damage_bonus == expected.get("damage_bonus", 0)
                assert _enum_value(actual.damage_type) == expected["damage_type"]


def test_special_zero_hp_poison_riders_are_source_bound_and_certified():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in ("giant-centipede", "giant-wasp"):
        monster = source[monster_id]
        source_attack = monster.attacks[0]
        expected = source_attack.on_hit_save_effect
        assert expected is not None
        assert supports_basic_attack_effects_2014(source_attack) is True
        assert basic_blockers_2014(monster) == ()
        runtime = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))[
            _attack_id(monster.id, source_attack.id)
        ].on_hit_save_damage
        assert runtime is not None and runtime.zero_hp_rider is not None
        rider = runtime.zero_hp_rider
        assert rider.stable is True
        assert list(rider.condition_ids) == expected["zero_hp_condition_ids"]
        assert rider.duration_rounds == expected["zero_hp_duration_rounds"]
