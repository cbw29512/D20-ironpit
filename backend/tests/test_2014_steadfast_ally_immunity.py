"""Conditional passive immunity uses live ally context, never unconditional protection."""
from app.combat.condition_immunity import condition_is_immune
from app.combat.opening_modifiers import opening_modifiers
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.passive_modifiers import PassiveModifierGrant


def test_steadfast_source_compiles_as_ally_qualified_immunity():
    monsters = {monster.id: monster for monster in load_monster_source_2014()}
    definition = adapt_basic_monster_2014(monsters["bearded-devil"])
    grant = next(item for item in definition.passive_modifier_grants if item.source_name == "Steadfast")
    assert grant.kind == "condition-immunity"
    assert grant.condition_id == "frightened"
    assert grant.requires_active_ally is True


def test_generic_ally_qualified_immunity_requires_live_context():
    monsters = {monster.id: monster for monster in load_monster_source_2014()}
    state = build_combatant_state(compile_combatant(adapt_basic_monster_2014(monsters["satyr"])))
    state.template.passive_modifier_grants = [PassiveModifierGrant(
        source_id="test-ally-ward", source_name="Ally Ward",
        kind="condition-immunity", condition_id="frightened", requires_active_ally=True,
    )]
    state.active_modifiers = opening_modifiers(state.template)
    assert not condition_is_immune(state, "frightened")
    assert condition_is_immune(state, "frightened", active_ally_present=True)
    assert not condition_is_immune(state, "charmed", active_ally_present=True)
    assert not condition_is_immune(state, "frightened", active_ally_present=False)


def test_condition_escalation_uses_same_live_ally_immunity_predicate():
    from app.combat.defensive_modifier_rules import condition_immunity_modifier_applies
    monsters = {monster.id: monster for monster in load_monster_source_2014()}
    state = build_combatant_state(compile_combatant(adapt_basic_monster_2014(monsters["satyr"])))
    state.template.passive_modifier_grants = [PassiveModifierGrant(
        source_id="test-ally-ward", source_name="Ally Ward",
        kind="condition-immunity", condition_id="frightened", requires_active_ally=True,
    )]
    state.active_modifiers = opening_modifiers(state.template)
    modifier = state.active_modifiers[0]
    assert not condition_immunity_modifier_applies(modifier, state, "frightened", None)
    assert condition_immunity_modifier_applies(
        modifier, state, "frightened", None, active_ally_present=True
    )
    assert not condition_immunity_modifier_applies(
        modifier, state, "frightened", None, active_ally_present=False
    )


def test_live_ally_predicate_changes_with_combatant_state():
    from app.combat.ally_context import has_active_ally
    from app.domain.encounters import EncounterCombatant, EncounterSetup
    monsters = {monster.id: monster for monster in load_monster_source_2014()}
    template = compile_combatant(adapt_basic_monster_2014(monsters["satyr"]))
    owner = EncounterCombatant(combatant_id="owner", side="monsters",
                               state=build_combatant_state(template))
    ally = EncounterCombatant(combatant_id="ally", side="monsters",
                              state=build_combatant_state(template))
    foe = EncounterCombatant(combatant_id="foe", side="heroes",
                             state=build_combatant_state(template))
    setup = EncounterSetup(heroes=[foe], monsters=[owner, ally],
                           hero_total_levels=1, monster_total_cr="1")
    assert has_active_ally(owner, setup)
    ally.state.current_hp = 0
    assert not has_active_ally(owner, setup)
    ally.state.current_hp = 1
    assert has_active_ally(owner, setup)
