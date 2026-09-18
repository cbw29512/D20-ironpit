from app.combat.conditional_attack_advantage import conditional_attack_advantage_sources
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import conditional_attack_advantage_2014

_BLOOD_FRENZY_IDS = (
    "giant-shark",
    "hunter-shark",
    "quipper",
    "swarm-of-quippers",
)


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_blood_frenzy_unlocks_all_trait_only_2014_candidates() -> None:
    source = _source()
    for monster_id in _BLOOD_FRENZY_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert attacks
        assert all(
            [spec.trigger for spec in attack.conditional_attack_advantage] == ["target_not_full_hp"]
            for attack in attacks
        )


def test_blood_frenzy_uses_shared_effective_max_hp_runtime() -> None:
    source = _source()
    shark = compile_combatant(adapt_basic_monster_2014(source["giant-shark"]))
    target = build_combatant_state(
        compile_combatant(adapt_basic_monster_2014(source["commoner"]))
    )
    assert conditional_attack_advantage_sources(shark.weapon_attack, target) == 0
    target.current_hp -= 1
    assert conditional_attack_advantage_sources(shark.weapon_attack, target) == 1


def test_blood_frenzy_binds_melee_but_not_ranged_attacks() -> None:
    sahuagin = _source()["sahuagin"]
    melee = next(attack for attack in sahuagin.attacks if attack.id == "spear")
    ranged = next(attack for attack in sahuagin.attacks if attack.id == "spear-ranged")
    assert [spec.trigger for spec in conditional_attack_advantage_2014(sahuagin, melee)] == [
        "target_not_full_hp"
    ]
    assert conditional_attack_advantage_2014(sahuagin, ranged) == []
