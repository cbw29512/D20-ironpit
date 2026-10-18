"""Regression tests for source-agnostic per-creature-turn reaction budgets."""
from app.combat.action_economy import is_available, spend
from app.combat.state import build_combatant_state, refresh_reactions_for_new_turn, refresh_start_of_turn
from app.domain.traits import CombatTrait
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_reactive_2014 import supports_reaction_each_turn_2014
from app.content.monster_basic_candidates_2014 import modeled_combat_traits_2014, unsupported_traits_2014, basic_blockers_2014
from app.content.roster import build_arena_roster


def test_source_trait_requires_matching_2014_clause():
    source = next(monster for monster in load_monster_source_2014() if monster.id == "marilith")
    assert supports_reaction_each_turn_2014(source)
    altered = source.model_copy(update={"source_traits": ""})
    assert not supports_reaction_each_turn_2014(altered)
    assert CombatTrait.REACTION_EACH_TURN in modeled_combat_traits_2014(source)
    assert "Reactive" not in unsupported_traits_2014(source)
    assert "source:trait" not in basic_blockers_2014(source)


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
    # A second creature turn restores only the source-declared budget.
    refresh_reactions_for_new_turn([reactive, ordinary, actor], ordinary)
    assert is_available(reactive, "reaction")
    assert not is_available(ordinary, "reaction")
    spend(reactive, "reaction")
    # The creature whose own turn is starting uses the normal refresh path.
    refresh_reactions_for_new_turn([reactive, ordinary, actor], reactive)
    assert not is_available(reactive, "reaction")
    refresh_start_of_turn(reactive)
    assert is_available(reactive, "reaction")
    # A fresh fight creates a separate reaction pool, not shared state.
    fresh = build_combatant_state(reactive.template)
    assert is_available(fresh, "reaction")
    spend(reactive, "reaction")
    assert is_available(fresh, "reaction")
