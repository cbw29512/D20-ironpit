from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def test_treant_animate_trees_is_arena_unavailable_summon() -> None:
    source = _source("treant")
    assert any(name.startswith("Animate Trees") for name in source.action_names)
    assert basic_blockers_2014(source) == ()
    assert "2014-treant" in {item.id for item in build_basic_2014_monsters()}
    template = compile_combatant(adapt_basic_monster_2014(source))
    names = {
        attack.weapon.name
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    }
    assert names >= {"Slam", "Rock"}


def test_nothic_weird_insight_is_arena_neutral_and_rotting_gaze_saves() -> None:
    source = _source("nothic")
    assert "Weird Insight" in source.action_names
    assert basic_blockers_2014(source) == ()
    assert "2014-nothic" in {item.id for item in build_basic_2014_monsters()}
    template = compile_combatant(adapt_basic_monster_2014(source))
    gaze = next(action for action in template.saving_throw_actions if action.name == "Rotting Gaze")
    assert gaze.save_ability == "constitution"
    assert gaze.dc == 12
    assert gaze.damage_dice_count == 3
    assert gaze.damage_dice_size == 6
    assert str(gaze.damage_type).split(".")[-1].casefold() == "necrotic"


def test_xday_and_legendary_remainders_stay_parked() -> None:
    parked = {
        "dretch": "source:extra-action",
        "knight": "source:extra-action",
        "aboleth": "source:legendary",
        "androsphinx": "mechanic:spellcasting",
        "gynosphinx": "mechanic:spellcasting",
    }
    for monster_id, blocker in parked.items():
        assert blocker in basic_blockers_2014(_source(monster_id))
