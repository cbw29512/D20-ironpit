from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.range import resolve_attack_roll_mode
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state
from app.combat.tactical_actions import choose_offensive_dash_grant
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.saving_throw_context import SavingThrowContext


def _source_by_id():
    return {monster.id: monster for monster in load_monster_source_2014()}


def _compile(monster_id: str):
    monster = _source_by_id()[monster_id]
    return compile_combatant(adapt_basic_monster_2014(monster))


def test_dark_devotion_unlocks_cultist_through_existing_save_advantage() -> None:
    source = _source_by_id()["cultist"]
    assert source.trait_names == ["Dark Devotion"]
    assert unsupported_traits_2014(source) == ()
    assert basic_blockers_2014(source) == ()

    template = _compile("cultist")
    grants = template.progression_features.saving_throw_advantage_grants
    assert {grant.source_name for grant in grants} == {"Dark Devotion"}
    assert {tuple(grant.required_effect_tags) for grant in grants} == {("charm",), ("frightened",)}

    charm = build_combatant_state(template)
    roll, _ = resolve_saving_throw(
        charm, "wisdom", 99, FixedDiceProvider([2, 17]),
        SavingThrowContext(effect_tags=frozenset({"charm"})),
    )
    assert roll is not None
    assert roll.mode == "advantage"
    assert roll.rolls == [2, 17]

    ordinary = build_combatant_state(template)
    roll, _ = resolve_saving_throw(ordinary, "wisdom", 99, FixedDiceProvider([10]))
    assert roll is not None
    assert roll.mode == "normal"
    assert roll.rolls == [10]


def test_aggressive_unlocks_orc_through_existing_offense_dash_grant() -> None:
    source = _source_by_id()["orc"]
    assert source.trait_names == ["Aggressive"]
    assert unsupported_traits_2014(source) == ()
    assert basic_blockers_2014(source) == ()

    template = _compile("orc")
    grants = template.bonus_tactical_action_grants
    assert len(grants) == 1
    assert grants[0].name == "Aggressive"
    assert grants[0].effects == ["dash"]
    assert grants[0].use_policy == "enable-offense"

    orc = EncounterCombatant(
        combatant_id="orc", side="monsters", position_ft=0, state=build_combatant_state(template),
    )
    target_template = _compile("commoner")
    commoner = EncounterCombatant(
        combatant_id="commoner", side="heroes", position_ft=50, state=build_combatant_state(target_template),
    )
    begin_turn(orc.state)
    setup = EncounterSetup(
        heroes=[commoner], monsters=[orc], hero_total_levels=1, monster_total_cr="1/2", ruleset="2014",
    )
    chosen = choose_offensive_dash_grant(orc, setup, "orc:1")
    assert chosen is not None
    assert chosen.name == "Aggressive"


def test_devils_sight_unlocks_lemure_as_arena_neutral() -> None:
    source = _source_by_id()["lemure"]
    assert "Devil's Sight" in source.trait_names
    assert "Hellish Rejuvenation" in source.trait_names
    assert unsupported_traits_2014(source) == ()
    assert basic_blockers_2014(source) == ()
    template = _compile("lemure")
    assert template.source_trait_names == source.trait_names
    assert template.id == "2014-lemure"


def test_two_heads_unlocks_ettin_and_death_dog() -> None:
    expected = {
        "death-dog": "Two-Headed",
        "ettin": "Two Heads",
    }
    roster_ids = {
        f"2014-{monster.id}"
        for monster in load_monster_source_2014()
        if not basic_blockers_2014(monster)
    }
    for monster_id, trait_name in expected.items():
        source = _source_by_id()[monster_id]
        assert trait_name in source.trait_names
        if monster_id == "ettin":
            assert "Wakeful" in source.trait_names
        assert unsupported_traits_2014(source) == ()
        assert basic_blockers_2014(source) == ()
        assert f"2014-{monster_id}" in roster_ids
        template = _compile(monster_id)
        grants = template.progression_features.saving_throw_advantage_grants
        assert {grant.source_name for grant in grants} == {trait_name}
        tagged = {tuple(grant.required_effect_tags) for grant in grants}
        assert tagged == {
            ("blinded",), ("charm",), ("charmed",), ("deafened",),
            ("frightened",), ("stunned",), ("unconscious",),
        }
        state = build_combatant_state(template)
        roll, _ = resolve_saving_throw(
            state, "wisdom", 99, FixedDiceProvider([2, 17]),
            SavingThrowContext(effect_tags=frozenset({"frightened"})),
        )
        assert roll is not None
        assert roll.mode == "advantage"
        ordinary, _ = resolve_saving_throw(state, "wisdom", 99, FixedDiceProvider([10]))
        assert ordinary is not None
        assert ordinary.mode == "normal"


def test_brave_binds_without_unlocking_remaining_knight_blockers() -> None:
    source = _source_by_id()["knight"]
    assert "Brave" in source.trait_names
    assert "Brave" not in unsupported_traits_2014(source)
    assert "source:trait" not in basic_blockers_2014(source)
    assert basic_blockers_2014(source) != ()


def test_cyclops_poor_depth_perception_reuses_printed_rock_range_disadvantage() -> None:
    source = _source_by_id()["cyclops"]
    assert "Poor Depth Perception" in source.trait_names
    assert "Poor Depth Perception" not in unsupported_traits_2014(source)
    assert basic_blockers_2014(source) == ()

    template = _compile("cyclops")
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    rock = next(item for item in attacks if item.weapon.name == "Rock")
    greatclub = next(item for item in attacks if item.weapon.name == "Greatclub")

    assert rock.weapon.normal_range_ft == 30
    assert rock.weapon.long_range_ft == 120
    assert greatclub.weapon.reach_ft == 10
    assert resolve_attack_roll_mode(rock.weapon, 30, close_enemy_active=False) is RollMode.NORMAL
    assert resolve_attack_roll_mode(rock.weapon, 35, close_enemy_active=False) is RollMode.DISADVANTAGE
