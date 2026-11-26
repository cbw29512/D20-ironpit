from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.offensive_spell_effects import build_guiding_bolt
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_phantasms_2014 import source_phantasms_action_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant
from app.domain.combatants import ResourceDefinition
from app.domain.environment_contexts import (
    EmittedEnvironmentContext, EnvironmentContextControlAction, EnvironmentContextMode,
)
from app.domain.encounters import EncounterSetup
from app.combat.environment_context_actions import resolve_environment_context_action


def _cards():
    cards = load_monster_source_2014()
    assert len(cards) == 327
    return cards


def test_semantic_327_card_scan_binds_only_complete_printed_phantasms():
    cards = _cards()
    applicable = [card for card in cards if source_phantasms_action_2014(card)]
    assert [(card.id, card.name) for card in applicable] == [("cloaker", "Cloaker")]
    action, = source_phantasms_action_2014(applicable[0])
    assert action.name == "Phantasms"
    assert action.resource_id == "phantasms"
    assert action.prohibited_environment_context_id == "bright_light"
    compiled = adapt_monster_mechanics_2014(applicable[0])
    assert action in compiled.timed_self_buff_actions
    assert ResourceDefinition(id="phantasms", name="Phantasms", max_uses=1) in compiled.resources
    assert action.illusory_duplicate_defense.redirection_mode == "uniform_original_and_duplicates"
    assert action.illusory_duplicate_defense.armor_class_mode == "source_armor_class"

    renamed = applicable[0].model_copy(update={"id": "renamed-source", "name": "Unrelated Aberration"})
    assert source_phantasms_action_2014(renamed) == [action]

    altered = applicable[0].model_copy(update={
        "source_actions": applicable[0].source_actions.replace(
            "three illusory duplicates", "two illusory duplicates",
        ),
    })
    assert source_phantasms_action_2014(altered) == []


def test_phantasms_weapon_interception_uses_uniform_selection_and_source_ac():
    cloaker_card = next(card for card in _cards() if card.id == "cloaker")
    action, = source_phantasms_action_2014(cloaker_card)
    cloaker_template = build_commoner().model_copy(update={
        "id": "cloaker", "name": "Cloaker", "armor_class": 14,
        "timed_self_buff_actions": [action],
        "resources": [ResourceDefinition(id="phantasms", name="Phantasms", max_uses=1)],
    })
    cloaker = EncounterCombatant(
        combatant_id="cloaker", side="monsters", position_ft=0,
        state=build_combatant_state(cloaker_template),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    resolve_timed_self_buff(1, 1, cloaker, action, affected_states=[cloaker.state])
    assert cloaker.state.timed_effects[0].illusory_duplicates_remaining == 3

    # d4=2 chooses a duplicate; the attack then hits the duplicate's printed AC 14.
    event = resolve_attack(
        2, 1, hero.state, cloaker.state, hero.state.template.weapon_attack,
        5, FixedDiceProvider([2, 12]), actor_event_id="hero", target_event_id="cloaker",
        affected_states=[hero.state, cloaker.state],
    )
    assert event.feature_id == "phantasms"
    assert event.feature_roll.notation == "1d4"
    assert event.target_ac == 14
    assert event.hit is True
    assert event.hp_before == event.hp_after == cloaker.state.current_hp
    assert cloaker.state.timed_effects[0].illusory_duplicates_remaining == 2

    hero.state.action_available = True
    before = cloaker.state.current_hp
    # d3=1 selects the original Cloaker, so the normal attack path deals damage.
    original = resolve_attack(
        3, 1, hero.state, cloaker.state, hero.state.template.weapon_attack,
        5, FixedDiceProvider([1, 19, 4]), actor_event_id="hero", target_event_id="cloaker",
        affected_states=[hero.state, cloaker.state],
    )
    assert original.feature_id != "phantasms"
    assert cloaker.state.current_hp < before
    assert cloaker.state.timed_effects[0].illusory_duplicates_remaining == 2


def test_phantasms_harmful_spell_attack_intercepts_without_damaging_source():
    cloaker_card = next(card for card in _cards() if card.id == "cloaker")
    action, = source_phantasms_action_2014(cloaker_card)
    cloaker_template = build_commoner().model_copy(update={
        "id": "cloaker", "name": "Cloaker", "armor_class": 14,
        "timed_self_buff_actions": [action],
        "resources": [ResourceDefinition(id="phantasms", name="Phantasms", max_uses=1)],
    })
    spell = build_guiding_bolt(5)
    caster_template = build_commoner().model_copy(update={
        "id": "caster", "name": "Caster", "spell_attack_actions": [spell],
        "resources": [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=1)],
    })
    cloaker = EncounterCombatant(
        combatant_id="cloaker", side="monsters", position_ft=30,
        state=build_combatant_state(cloaker_template),
    )
    caster = EncounterCombatant(
        combatant_id="caster", side="heroes", position_ft=0,
        state=build_combatant_state(caster_template),
    )
    setup = EncounterSetup(
        heroes=[caster], monsters=[cloaker], hero_total_levels=1, monster_total_cr="8",
    )
    resolve_timed_self_buff(1, 1, cloaker, action, affected_states=[cloaker.state])
    hp_before = cloaker.state.current_hp

    # d4=2 chooses a duplicate; 12+5 hits its source AC 14. No spell damage or
    # Guiding Bolt rider reaches the Cloaker, while the slot and Action are spent.
    event = resolve_spell_attack(
        2, 1, caster, cloaker, spell, setup, "1:caster", FixedDiceProvider([2, 12]),
    )

    assert event.attack_id == "guiding-bolt"
    assert event.feature_id == "phantasms"
    assert event.feature_roll.notation == "1d4"
    assert event.target_ac == 14
    assert event.hit is True
    assert event.damage_roll is None
    assert event.hp_before == event.hp_after == hp_before == cloaker.state.current_hp
    assert cloaker.state.timed_effects[0].illusory_duplicates_remaining == 2
    assert cloaker.state.active_modifiers == []
    assert caster.state.resources[0].current_uses == 0
    assert caster.state.action_available is False
    assert "Caster: HIT with Guiding Bolt against Cloaker's Phantasms duplicate" in event.description

def test_phantasms_cannot_start_in_bright_light_and_expires_when_light_appears():
    card = next(card for card in _cards() if card.id == "cloaker")
    action, = source_phantasms_action_2014(card)
    cloaker_template = build_commoner().model_copy(update={
        "id": "cloaker", "name": "Cloaker", "timed_self_buff_actions": [action],
        "resources": [ResourceDefinition(id="phantasms", name="Phantasms", max_uses=1)],
    })
    light_action = EnvironmentContextControlAction(
        id="illumination", name="Illumination", action_cost="bonus_action",
        initial_mode_id="dark", ai_mode_id="bright",
        modes=[
            EnvironmentContextMode(id="dark"),
            EnvironmentContextMode(id="bright", emitted_contexts=[
                EmittedEnvironmentContext(context_id="bright_light", radius_ft=30),
            ]),
        ],
    )
    light_template = build_commoner().model_copy(update={
        "id": "light-source", "name": "Light Source",
        "environment_context_control_actions": [light_action],
    })
    cloaker = EncounterCombatant(
        combatant_id="cloaker", side="monsters", position_ft=10,
        state=build_combatant_state(cloaker_template),
    )
    light = EncounterCombatant(
        combatant_id="light", side="heroes", position_ft=0,
        state=build_combatant_state(light_template),
    )
    setup = EncounterSetup(
        heroes=[light], monsters=[cloaker], hero_total_levels=1, monster_total_cr="8",
    )
    resolve_timed_self_buff(1, 1, cloaker, action, setup=setup, affected_states=[cloaker.state, light.state])
    assert cloaker.state.timed_effects[0].illusory_duplicates_remaining == 3

    bright = next(mode for mode in light_action.modes if mode.id == "bright")
    event = resolve_environment_context_action(
        2, 1, light, light_action, bright,
        affected_states=[light.state, cloaker.state], setup=setup,
    )
    assert cloaker.state.timed_effects == []
    assert "Cloaker's Phantasms ends" in event.description

    cloaker.state.action_available = True
    next(resource for resource in cloaker.state.resources if resource.id == "phantasms").current_uses = 1
    light.state.bonus_action_available = True
    light.state.environment_context_modes[light_action.id] = "bright"
    try:
        resolve_timed_self_buff(
            3, 1, cloaker, action, setup=setup,
            affected_states=[cloaker.state, light.state],
        )
    except ValueError as exc:
        assert "cannot be activated in bright light" in str(exc)
    else:
        raise AssertionError("Phantasms must fail closed in bright light")
