"""Regression tests for source-agnostic per-creature-turn reaction budgets."""
from app.combat.action_economy import is_available, spend
from app.combat.state import build_combatant_state, refresh_reactions_for_new_turn, refresh_start_of_turn
from app.domain.traits import CombatTrait
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_reactive_2014 import supports_reaction_each_turn_2014
from app.content.monster_basic_candidates_2014 import modeled_combat_traits_2014
from app.content.roster import build_arena_roster


def test_source_trait_requires_matching_2014_clause():
    source = next(monster for monster in load_monster_source_2014() if monster.id == "marilith")
    assert supports_reaction_each_turn_2014(source)
    altered = source.model_copy(update={"source_traits": ""})
    assert not supports_reaction_each_turn_2014(altered)
    assert CombatTrait.REACTION_EACH_TURN in modeled_combat_traits_2014(source)


def test_reaction_budget_refreshes_only_for_declared_generic_trait():
    template = build_arena_roster().monsters[0]
    reactive = build_combatant_state(template.model_copy(update={
        "name": "Unrelated synthetic combatant",
        "combat_traits": [*template.combat_traits, CombatTrait.REACTION_EACH_TURN],
    }))
    ordinary = build_combatant_state(template.model_copy(update={"name": "Ordinary combatant"}))
    actor = build_combatant_state(template.model_copy(update={"name": "Acting combatant"}))
    spend(reactive, "reaction")
    spend(ordinary, "reaction")
    refresh_reactions_for_new_turn([reactive, ordinary, actor], actor)
    assert is_available(reactive, "reaction")
    assert not is_available(ordinary, "reaction")
    spend(reactive, "reaction")
    assert not is_available(reactive, "reaction")
    refresh_start_of_turn(reactive)
    assert is_available(reactive, "reaction")
