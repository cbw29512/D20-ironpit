from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.combat.instant_death import apply_terminal_effect_tag
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import terminal_effect_tags_2014
from scripts.browser_template_serializer import template_row


_TRAIT = "Antimagic Susceptibility"
_FAMILY = {"Animated Armor", "Flying Sword", "Rug of Smothering"}
_NEWLY_READY = {"Animated Armor", "Flying Sword"}


def _source_by_name():
    return {monster.name: monster for monster in load_monster_source_2014()}


def test_antimagic_susceptibility_binds_exact_2014_source_family() -> None:
    source = _source_by_name()
    actual = {
        monster.name for monster in source.values()
        if _TRAIT in monster.trait_names
    }
    assert actual == _FAMILY

    for name in _FAMILY:
        monster = source[name]
        assert terminal_effect_tags_2014(monster) == ["antimagic"]
        assert _TRAIT not in unsupported_traits_2014(monster)


def test_antimagic_family_unlocks_only_the_two_single_blocker_constructs() -> None:
    source = _source_by_name()
    for name in _NEWLY_READY:
        monster = source[name]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.terminal_effect_tags == ["antimagic"]
        assert _TRAIT in template.source_trait_names
        assert template_row(template)["terminal_effect_tags"] == ["antimagic"]

    rug = source["Rug of Smothering"]
    assert basic_blockers_2014(rug)
    assert _TRAIT not in unsupported_traits_2014(rug)


def test_antimagic_tag_immediately_applies_terminal_dead_state() -> None:
    armor = _source_by_name()["Animated Armor"]
    template = compile_combatant(adapt_basic_monster_2014(armor))
    state = build_combatant_state(template)
    state.active_effect_ids.append("dodge")

    assert apply_terminal_effect_tag(state, "antimagic") == "dead"
    assert state.current_hp == 0
    assert state.is_alive is False
    assert state.is_dead is True
    assert state.is_unconscious is False
    assert state.is_stable is False
    assert "dodge" not in state.active_effect_ids


def test_unrelated_effect_tag_does_not_trigger_antimagic_susceptibility() -> None:
    armor = _source_by_name()["Animated Armor"]
    state = build_combatant_state(compile_combatant(adapt_basic_monster_2014(armor)))

    assert apply_terminal_effect_tag(state, "fire") == "not_susceptible"
    assert state.current_hp == state.template.max_hp
    assert state.is_alive is True
    assert state.is_dead is False
