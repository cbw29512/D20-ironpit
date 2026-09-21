from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.models import RollMode


def _source_spy():
    return next(monster for monster in load_monster_source_2014() if monster.name == "Spy")


def _runtime_spy():
    return next(monster for monster in build_basic_2014_monsters() if monster.name == "Spy")


def test_2014_spy_source_traits_bind_without_name_specific_engine_logic() -> None:
    source = _source_spy()

    assert source.trait_names == ["Cunning Action", "Sneak Attack (1/Turn)"]
    assert "extra 7 (2d6) damage" in (source.source_traits or "")
    assert basic_blockers_2014(source) == ()


def test_2014_spy_compiles_shared_cunning_action_and_sneak_attack_data() -> None:
    spy = _runtime_spy()
    attacks = [spy.weapon_attack, *spy.alternate_weapon_attacks]

    assert spy.ruleset == "2014"
    assert spy.progression_features.cunning_action is True
    assert spy.progression_features.sneak_attack_d6 == 2
    assert {attack.weapon.name for attack in attacks} == {"Shortsword", "Hand Crossbow"}
    assert all(attack.sneak_attack_eligible for attack in attacks)
    assert spy.attack_action is not None
    assert [slot.attack_ids for slot in spy.attack_action.slots] == [
        ["2014-spy-shortsword"],
        ["2014-spy-shortsword"],
    ]


def test_2014_spy_sneak_attack_rolls_two_d6_once_per_turn() -> None:
    state = build_combatant_state(_runtime_spy())
    attack = state.template.weapon_attack

    _, components = resolve_weapon_damage(
        state,
        attack,
        FixedDiceProvider([4, 5, 6]),
        False,
        RollMode.ADVANTAGE,
        turn_key="1:spy",
    )
    sneak = next(component for component in components if component.source == "Sneak Attack")
    assert sneak.notation == "2d6+0"
    assert sneak.rolls == [5, 6]

    _, second_components = resolve_weapon_damage(
        state,
        attack,
        FixedDiceProvider([3]),
        False,
        RollMode.ADVANTAGE,
        turn_key="1:spy",
    )
    assert all(component.source != "Sneak Attack" for component in second_components)
