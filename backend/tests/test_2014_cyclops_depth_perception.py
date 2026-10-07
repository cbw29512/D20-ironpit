from __future__ import annotations

from app.combat.distance_attack_disadvantage import distance_attack_disadvantage_sources
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import attack_disadvantage_beyond_ft_2014
from scripts.browser_template_serializer import template_row


def _source():
    return next(item for item in load_monster_source_2014() if item.id == "cyclops")


def test_cyclops_poor_depth_perception_binds_distance_threshold() -> None:
    source = _source()
    assert "Poor Depth Perception" in source.trait_names
    assert attack_disadvantage_beyond_ft_2014(source) == 30
    assert basic_blockers_2014(source) == ()

    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.progression_features.attack_disadvantage_beyond_ft == 30
    assert template_row(template)["attack_disadvantage_beyond_ft"] == 30


def test_distance_attack_disadvantage_respects_threshold() -> None:
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    state = build_combatant_state(template)
    assert distance_attack_disadvantage_sources(state, 30) == 0
    assert distance_attack_disadvantage_sources(state, 31) == 1
    assert distance_attack_disadvantage_sources(state, 120) == 1
