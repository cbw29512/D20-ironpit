from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_conditional_attack_advantage_2014 import conditional_attack_advantage_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source_by_name():
    return {monster.name: monster for monster in load_monster_source_2014()}


def test_blood_frenzy_binds_only_to_melee_attacks() -> None:
    source = _source_by_name()
    for name in ("Giant Shark", "Sahuagin"):
        monster = source[name]
        assert "Blood Frenzy" in monster.trait_names
        assert "Blood Frenzy" not in unsupported_traits_2014(monster)
        for attack in monster.attacks:
            specs = conditional_attack_advantage_2014(monster, attack)
            if attack.kind == "melee":
                assert [spec.trigger for spec in specs] == ["target_not_full_hp"]
            else:
                assert specs == []


def test_giant_shark_is_admitted_with_raw_blood_frenzy() -> None:
    giant_shark = _source_by_name()["Giant Shark"]
    assert basic_blockers_2014(giant_shark) == ()
    template = compile_combatant(adapt_basic_monster_2014(giant_shark))
    assert template.ruleset == "2014"
    assert template.name == "Giant Shark"
    assert any(
        spec.trigger == "target_not_full_hp"
        for attack in template.attacks
        for spec in attack.conditional_attack_advantage
    )
