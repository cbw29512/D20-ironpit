from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


_FIXED_DAMAGE_IDS = {
    "badger", "cat", "crab", "hawk", "lizard", "rat", "weasel",
}


def test_fixed_damage_only_batch_is_admitted_and_compiles():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _FIXED_DAMAGE_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        definition = adapt_basic_monster_2014(monster)
        template = compile_combatant(definition)
        assert template.ruleset == "2014"
        assert len(definition.attacks) == len(monster.attacks)
        for source_attack, adapted_attack, compiled_attack in zip(
            monster.attacks, definition.attacks, template.attacks, strict=True
        ):
            assert source_attack.damage.dice_count == 0
            assert adapted_attack.damage is None
            assert adapted_attack.fixed_damage == source_attack.damage.average
            assert compiled_attack.fixed_damage == source_attack.damage.average


def test_fixed_damage_batch_raises_roster_to_at_least_39():
    ready = [monster for monster in load_monster_source_2014() if not basic_blockers_2014(monster)]
    assert len(ready) >= 39
