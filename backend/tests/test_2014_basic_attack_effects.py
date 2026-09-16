from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_attack_effects_2014 import supports_basic_attack_effects_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


_ATTACK_EFFECT_IDS = {
    "constrictor-snake", "crocodile", "flying-snake", "giant-constrictor-snake",
    "giant-crab", "roc", "tyrannosaurus-rex",
}
_SAVE_PRONE_IDS = {
    "ankylosaurus", "dire-wolf", "giant-crocodile", "mastiff", "wolf", "worg",
}
_SAVE_DAMAGE_IDS = {
    "giant-poisonous-snake", "giant-scorpion", "poisonous-snake", "scorpion", "wyvern",
}


def _attack_id(monster_id: str, attack_id: str) -> str:
    return f"2014-{monster_id}-{attack_id}".replace("--", "-")


def _runtime_attacks(template):
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return {attack.id: attack for attack in attacks}


def _enum_value(value):
    return value.value if hasattr(value, "value") else value


def test_basic_attack_effect_tranche_is_exactly_78_and_ruleset_isolated():
    source = load_monster_source_2014()
    ready = [monster for monster in source if not basic_blockers_2014(monster)]
    assert len(ready) == 78
    assert _ATTACK_EFFECT_IDS | _SAVE_PRONE_IDS | _SAVE_DAMAGE_IDS <= {monster.id for monster in ready}
    for monster in ready:
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.ruleset == "2014"
        assert template.id == f"2014-{monster.id}"


def test_basic_attack_effects_preserve_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _ATTACK_EFFECT_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        runtime_attacks = _runtime_attacks(template)
        for source_attack in monster.attacks:
            runtime = runtime_attacks[_attack_id(monster.id, source_attack.id)]
            expected_damage = source_attack.on_hit_damage
            assert len(runtime.on_hit_damage) == len(expected_damage)
            for expected, actual in zip(expected_damage, runtime.on_hit_damage, strict=True):
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
                expected_size = expected_control.get("max_target_size")
                actual_size = runtime.control_effect.max_target_size
                assert (_enum_value(actual_size) if actual_size else None) == (
                    str(expected_size).lower() if expected_size is not None else None
                )
            assert runtime.forbid_target_grappled_by_self == source_attack.forbid_target_grappled_by_self


def test_save_to_prone_riders_preserve_exact_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _SAVE_PRONE_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        save_attacks = [attack for attack in monster.attacks if attack.on_hit_save_effect is not None]
        assert save_attacks
        for source_attack in save_attacks:
            expected = source_attack.on_hit_save_effect
            runtime = runtime_attacks[_attack_id(monster.id, source_attack.id)].on_hit_condition_save
            assert expected is not None and runtime is not None
            assert _enum_value(runtime.save_ability) == str(expected["save_ability"]).lower()
            assert runtime.dc == expected["dc"]
            assert runtime.condition_id == "prone"
            expected_size = expected.get("max_target_size")
            assert (_enum_value(runtime.max_target_size) if runtime.max_target_size else None) == (
                str(expected_size).lower() if expected_size is not None else None
            )


def test_save_damage_riders_preserve_exact_pinned_source_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _SAVE_DAMAGE_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        runtime_attacks = _runtime_attacks(compile_combatant(adapt_basic_monster_2014(monster)))
        save_attacks = [attack for attack in monster.attacks if attack.on_hit_save_effect is not None]
        assert save_attacks
        for source_attack in save_attacks:
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


def test_special_zero_hp_poison_and_charge_riders_still_fail_closed():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    centipede = source["giant-centipede"].attacks[0]
    wasp = source["giant-wasp"].attacks[0]
    elk_ram = source["elk"].attacks[0]
    assert "zero_hp_condition_ids" in centipede.on_hit_save_effect
    assert "zero_hp_condition_ids" in wasp.on_hit_save_effect
    assert elk_ram.charge_profile is not None
    assert supports_basic_attack_effects_2014(centipede) is False
    assert supports_basic_attack_effects_2014(wasp) is False
    assert supports_basic_attack_effects_2014(elk_ram) is False
    assert basic_blockers_2014(source["giant-centipede"]) == ("attack:complex",)
    assert basic_blockers_2014(source["giant-wasp"]) == ("attack:complex",)
    assert basic_blockers_2014(source["elk"]) == ("attack:complex",)
