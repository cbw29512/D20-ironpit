from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_damage_taken_effects_2014 import damage_taken_timed_effects_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.weapons import DamageType


def _flesh_golem():
    return next(monster for monster in load_monster_source_2014() if monster.id == "flesh-golem")


def test_flesh_golem_aversion_of_fire_reuses_fire_disadvantage_binding() -> None:
    source = _flesh_golem()
    assert "Aversion of Fire" in source.trait_names

    rules = damage_taken_timed_effects_2014(source)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.source_id == "flesh-golem-aversion-of-fire"
    assert rule.source_name == "Aversion of Fire"
    assert rule.trigger_damage_type is DamageType.FIRE
    assert rule.target_turns == 1
    assert rule.attack_roll_disadvantage is True
    assert rule.ability_check_disadvantage is True


def test_aversion_is_resolved_while_berserk_remains_the_flesh_golem_trait_blocker() -> None:
    source = _flesh_golem()
    unsupported = set(unsupported_traits_2014(source))
    assert "Aversion of Fire" not in unsupported
    assert unsupported == {"Berserk"}
    assert basic_blockers_2014(source) == ("source:trait",)
