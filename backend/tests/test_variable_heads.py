"""Integration coverage for source-bound variable heads in both combat layers."""
from app.combat.attack_action_sequences import expanded_sequence_slots
from app.combat.state import build_combatant_state
from app.combat.variable_heads import end_owner_turn, spend_opportunity_reaction
from app.combat.zero_hp import apply_damage
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.attack_action_definitions import AttackActionVariant
from app.domain.models import DamageType


def hydra_template():
    source = next(item for item in load_monster_source_2014() if item.id == "hydra")
    assert basic_blockers_2014(source) == ()
    return compile_combatant(adapt_basic_monster_2014(source))


def test_hydra_card_compiles_to_generic_profile_and_dynamic_queue():
    template = hydra_template()
    state = build_combatant_state(template)
    assert state.current_heads == 5
    assert state.opportunity_reactions_remaining == 4
    assert template.attack_action.repeat_count_from_variable_heads is True
    variant = AttackActionVariant(
        id=template.attack_action.id, slots=template.attack_action.slots,
    )
    slots, roll = expanded_sequence_slots(variant, None, state)
    assert roll is None
    assert len(slots) == 5
    state.current_heads = 3
    slots, _ = expanded_sequence_slots(variant, None, state)
    assert len(slots) == 3


def test_damage_severs_once_per_turn_and_fire_blocks_regrowth():
    state = build_combatant_state(hydra_template())
    assert apply_damage(state, 15, damage_types={DamageType.SLASHING}) == "damaged"
    assert state.current_heads == 5
    apply_damage(state, 10, damage_types={DamageType.SLASHING})
    assert state.current_heads == 4
    apply_damage(state, 100, damage_types={DamageType.BLUDGEONING})
    assert state.current_heads == 4

    state.damage_taken_this_turn_by_type = {}
    apply_damage(state, 25, damage_types={DamageType.FIRE})
    assert state.current_heads == 3
    assert end_owner_turn(state) == (0, 0)
    assert state.current_heads == 3


def test_regrowth_heals_and_reactions_are_opportunity_only():
    state = build_combatant_state(hydra_template())
    apply_damage(state, 25, damage_types={DamageType.SLASHING})
    state.damage_taken_this_turn_by_type = {}
    grown, healed = end_owner_turn(state)
    assert (grown, healed) == (2, 20)
    assert state.current_heads == 6

    assert state.reaction_available is True
    spend_opportunity_reaction(state)
    assert state.reaction_available is False
    assert state.opportunity_reactions_remaining == 4
    spend_opportunity_reaction(state)
    assert state.opportunity_reactions_remaining == 3


def test_losing_last_head_kills_creature():
    state = build_combatant_state(hydra_template())
    state.current_heads = 1
    outcome = apply_damage(state, 25, damage_types={DamageType.SLASHING})
    assert outcome == "dead"
    assert state.is_dead is True
