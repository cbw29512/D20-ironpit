"""Source-neutral lifecycle coverage for declarative variable heads."""
from app.combat.state import build_combatant_state
from app.combat.variable_heads import end_owner_turn, spend_opportunity_reaction
from app.combat.zero_hp import apply_damage
from app.content.monsters import build_commoner
from app.domain.models import DamageType
from app.domain.variable_heads import VariableHeadProfile


def _state():
    profile = VariableHeadProfile(
        source_name="Printed Head Lifecycle", reaction_source_name="Printed Extra Reactions",
        initial_heads=5, sever_damage_threshold=25, heads_per_regrowth=2,
        healing_per_regrown_head=10, regrowth_blocking_damage_types=["fire"],
    )
    template = build_commoner().model_copy(update={"max_hp": 200, "variable_heads": profile})
    return build_combatant_state(template)


def test_damage_severs_once_per_turn_and_fire_blocks_regrowth():
    state = _state()
    apply_damage(state, 15, damage_types={DamageType.SLASHING})
    apply_damage(state, 10, damage_types={DamageType.SLASHING})
    assert state.current_heads == 4
    apply_damage(state, 100, damage_types={DamageType.BLUDGEONING})
    assert state.current_heads == 4
    state.damage_taken_this_turn_by_type = {}
    apply_damage(state, 25, damage_types={DamageType.FIRE})
    assert end_owner_turn(state) == (0, 0)
    assert state.current_heads == 3


def test_regrowth_heals_and_extra_reactions_are_opportunity_only():
    state = _state()
    apply_damage(state, 25, damage_types={DamageType.SLASHING})
    state.damage_taken_this_turn_by_type = {}
    assert end_owner_turn(state) == (2, 20)
    assert state.current_heads == 6
    spend_opportunity_reaction(state)
    assert state.reaction_available is False
    spend_opportunity_reaction(state)
    assert state.opportunity_reactions_remaining == 4


def test_losing_last_head_kills_creature():
    state = _state()
    state.current_heads = 1
    assert apply_damage(state, 25, damage_types={DamageType.SLASHING}) == "dead"
    assert state.is_dead is True


def test_multiple_heads_grant_save_advantage_against_listed_conditions():
    from app.combat.defensive_modifier_rules import saving_throw_advantage_sources
    from app.domain.saving_throw_context import SavingThrowContext
    state = _state()
    state.current_heads = 3
    profile = state.template.variable_heads.model_copy(update={"save_advantage_conditions": ["blinded", "charmed"]})
    state.template = state.template.model_copy(update={"variable_heads": profile})
    context = SavingThrowContext(condition_id="blinded")
    assert saving_throw_advantage_sources(state, "wisdom", context) >= 1
    context_other = SavingThrowContext(condition_id="poisoned")
    assert saving_throw_advantage_sources(state, "constitution", context_other) == 0
    state.current_heads = 1
    assert saving_throw_advantage_sources(state, "wisdom", context) == 0
