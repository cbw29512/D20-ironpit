from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.traits import CombatTrait


def _source_by_id():
    return {monster.id: monster for monster in load_monster_source_2014()}


def _state(monster_id: str):
    monster = _source_by_id()[monster_id]
    return build_combatant_state(compile_combatant(adapt_basic_monster_2014(monster)))


def test_sure_footed_source_binding_unlocks_goats_but_not_mule() -> None:
    source = _source_by_id()
    for monster_id in ("goat", "giant-goat"):
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert CombatTrait.SURE_FOOTED in template.combat_traits

    mule = source["mule"]
    assert unsupported_traits_2014(mule) == ("Beast of Burden",)
    assert basic_blockers_2014(mule) == ("source:trait",)


def test_sure_footed_advantage_is_limited_to_prone_strength_dexterity_saves() -> None:
    context = SavingThrowContext(condition_id="prone")

    strength = _state("goat")
    roll, _ = resolve_saving_throw(strength, "strength", 99, FixedDiceProvider([2, 15]), context)
    assert roll is not None
    assert roll.mode == "advantage"
    assert roll.rolls == [2, 15]

    dexterity = _state("goat")
    roll, _ = resolve_saving_throw(dexterity, "dexterity", 99, FixedDiceProvider([3, 14]), context)
    assert roll is not None
    assert roll.mode == "advantage"
    assert roll.rolls == [3, 14]

    unrelated = _state("goat")
    roll, _ = resolve_saving_throw(unrelated, "strength", 99, FixedDiceProvider([10]))
    assert roll is not None
    assert roll.mode == "normal"
    assert roll.rolls == [10]

    constitution = _state("goat")
    roll, _ = resolve_saving_throw(constitution, "constitution", 99, FixedDiceProvider([11]), context)
    assert roll is not None
    assert roll.mode == "normal"
    assert roll.rolls == [11]
