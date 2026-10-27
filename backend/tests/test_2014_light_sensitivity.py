"""Source-verified 2014 Light Sensitivity binds to bright-light context reaction.

No default bright light is invented; the permanent reaction stays inactive
until a supported effect emits the bright_light context.
"""
from __future__ import annotations

from app.content.environment_context_reactions import (
    bright_light_sensitivity_2014, verified_bright_light_sensitivity_2014,
)
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_environment_context_bindings_2014 import environment_context_reactions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014


def _monster(monster_id: str):
    return next(m for m in load_monster_source_2014() if m.id == monster_id)


def test_cloaker_light_sensitivity_source_binds_to_bright_light_reaction() -> None:
    monster = _monster("cloaker")
    assert verified_bright_light_sensitivity_2014(monster)
    reactions = environment_context_reactions_2014(monster)
    sensitivity = next(r for r in reactions if r.source_name == "Light Sensitivity")
    assert sensitivity.context_id == "bright_light"
    assert sensitivity.disadvantage_on == ["attack_rolls", "sight_based_perception_checks"]
    assert "Light Sensitivity" in bound_trait_names_2014(monster)
    assert "Light Sensitivity" not in unsupported_traits_2014(monster)
    # Mutation fails closed.
    mutated = monster.model_copy(update={"source_traits": monster.source_traits.replace("bright light", "dim light")})
    assert not verified_bright_light_sensitivity_2014(mutated)
