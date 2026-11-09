"""2014 source-owned helper rescue through one universal ability-check resolver."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import apply_grapple
from app.combat.grapple_helper_rescue import (
    choose_grapple_helper_rescue, resolve_grapple_helper_rescue,
)
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_grapple_rescue_2014 import source_grapple_rescue_rules_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import EncounterSelection
from scripts.browser_template_serializer import template_row


def _cards():
    return {card.id: card for card in load_monster_source_2014()}


def _setup():
    card = _cards()["water-elemental"]
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(
            compile_combatant(adapt_monster_mechanics_2014(card))),
    )
    # The 2024 demo fighter intentionally lacks authoritative ability scores.
    # Use a certified 2014 pregen for a real source-correct Strength check.
    hero = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    )).heroes[0].state.template
    assert hero.ruleset == "2014" and hero.ability_scores is not None
    helper = EncounterCombatant(
        combatant_id="helper", side="heroes", position_ft=5,
        state=build_combatant_state(hero),
    )
    held = EncounterCombatant(
        combatant_id="held", side="heroes", position_ft=0,
        state=build_combatant_state(hero),
    )
    setup = EncounterSetup(
        heroes=[helper, held], monsters=[owner],
        ruleset="2014", hero_total_levels=2, monster_total_cr="5",
    )
    apply_grapple(
        held.state, owner.combatant_id, 14, 0,
        restrains=True, prevents_breathing=True, linked_effect_id="whelm",
    )
    return helper, held, owner, setup


def test_full_catalog_proves_one_helper_rule_and_browser_uses_exact_values():
    cards = _cards()
    assert len(cards) == 327
    found = {
        card.id: rules for card in cards.values()
        if (rules := source_grapple_rescue_rules_2014(card))
    }
    assert set(found) == {"water-elemental"}
    (rule,) = found["water-elemental"]
    assert (rule.source_action_id, rule.source_name) == ("whelm", "Whelm")
    assert (rule.check_ability, rule.check_dc, rule.helper_range_ft) == (
        "strength", 14, 5,
    )
    template = compile_combatant(adapt_monster_mechanics_2014(cards["water-elemental"]))
    assert template.grapple_rescue_rules == [rule]
    assert template_row(template)["grapple_rescue_rules"] == [rule.model_dump(mode="json")]


def test_source_mutation_fails_closed_and_valid_numeric_helper_range_rebinds():
    card = _cards()["water-elemental"]
    edited = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "can pull a creature or object out of it",
            "can pull a creature, object, or spell out of it",
        ),
    })
    assert source_grapple_rescue_rules_2014(edited) == []
    ranged = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "A creature within 5 feet", "A creature within 10 feet",
        ),
    })
    assert source_grapple_rescue_rules_2014(ranged)[0].helper_range_ft == 10
    renamed = card.model_copy(update={
        "name": "Synthetic Fluid", "id": "synthetic-fluid",
        "source_actions": card.source_actions.replace(
            "Whelm (Recharge 4–6)", "Undertow (Recharge 4–6)",
        ),
        "action_names": [
            text.replace("Whelm (Recharge 4–6)", "Undertow (Recharge 4–6)")
            for text in card.action_names
        ],
        "action_recharges": {"undertow": 4},
    })
    (rule,) = source_grapple_rescue_rules_2014(renamed)
    assert (rule.source_action_id, rule.source_name) == ("undertow", "Undertow")


def test_rescue_success_consumes_helper_action_releases_held_ally_and_logs_source():
    helper, held, owner, setup = _setup()
    choice = choose_grapple_helper_rescue(helper, setup)
    assert choice is not None
    source, victim, rule = choice
    assert source == owner and victim == held
    mismatched_rule = rule.model_copy(update={"source_action_id": "other-source-action"})
    from app.combat.grapple_helper_rescue import eligible
    assert not eligible(helper, held, owner, mismatched_rule)
    held.state.grapple_sources[0].linked_effect_id = "different-action"
    assert not eligible(helper, held, owner, rule)
    held.state.grapple_sources[0].linked_effect_id = "whelm"
    assert eligible(helper, held, owner, rule)
    event = resolve_grapple_helper_rescue(
        1, 1, helper, held, owner, rule, FixedDiceProvider([20]), setup,
    )
    assert event.check_succeeded is True
    assert event.check_dc == 14
    assert event.feature_id == "whelm" and "Whelm" in event.description
    assert helper.state.action_available is False
    assert held.state.grapple_sources == []
    assert not ({"grappled", "restrained"} & set(held.state.active_effect_ids))


def test_rescue_failure_uses_action_but_keeps_grapple_and_range_is_source_owned():
    helper, held, owner, setup = _setup()
    rule = owner.state.template.grapple_rescue_rules[0]
    event = resolve_grapple_helper_rescue(
        1, 1, helper, held, owner, rule, FixedDiceProvider([1]), setup,
    )
    assert event.check_succeeded is False
    assert helper.state.action_available is False
    assert held.state.grapple_sources[0].source_id == owner.combatant_id
    helper.state.action_available = True
    helper.position_ft = 15
    assert choose_grapple_helper_rescue(helper, setup) is None
