"""Generic third-party/held-target Strength Action breaks source-linked Grapples."""
from __future__ import annotations

import logging

from app.combat.conditions import apply_hit_conditions
from app.combat.grapple_appendage_capacity import source_grapple_capacity_used
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple_helper_rescue import (
    choose_grapple_helper_rescue, eligible, resolve_grapple_helper_rescue,
)
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_breakable_grapple_rescue_2014 import (
    source_breakable_grapple_rescue_rules_2014,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import EncounterSelection
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _fixture():
    try:
        cards = load_monster_source_2014()
        source = next(item for item in cards if item.id == "roper")
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        attack = next(item for item in [
            template.weapon_attack, *template.alternate_weapon_attacks
        ] if item and item.id == "2014-roper-tendril")
        rule = template.grapple_rescue_rules[0]
        hero_template = build_encounter_setup(EncounterSelection(
            ruleset="2014", hero_ids=["karnok-stoneward-2014-l1"],
            monster_ids=["2014-goblin"],
        )).heroes[0].state.template
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        held = EncounterCombatant(
            combatant_id="held", side="heroes", position_ft=40,
            state=build_combatant_state(hero_template),
        )
        helper = EncounterCombatant(
            combatant_id="helper", side="heroes", position_ft=45,
            state=build_combatant_state(hero_template),
        )
        setup = EncounterSetup(
            heroes=[held, helper], monsters=[owner], ruleset="2014",
            hero_total_levels=2, monster_total_cr="5",
        )
        return source, attack, rule, held, helper, owner, setup
    except Exception:
        logger.exception("Failed Roper linked-break Action fixture.")
        raise


def test_printed_break_action_is_source_proven_and_browser_exported():
    try:
        source, attack, rule, held, helper, owner, setup = _fixture()
        original = source.model_dump_json()
        assert rule == source_breakable_grapple_rescue_rules_2014(source)[0]
        assert (rule.source_action_id, rule.source_name) == (attack.id, "Tendril")
        assert (rule.check_ability, rule.check_dc, rule.helper_range_ft) == (
            "strength", 15, 5,
        )
        assert rule.allow_held_target and rule.requires_breakable_object
        assert rule.helper_range_anchor == "held_target"
        assert rule.release_verb == "break"
        assert template_row(owner.state.template)["grapple_rescue_rules"] == [
            rule.model_dump(mode="json")
        ]
        bad = source.model_copy(update={
            "source_traits": source.source_traits.replace(
                "DC 15 Strength check against it", "DC 20 Strength check against it",
            ),
        })
        assert source_breakable_grapple_rescue_rules_2014(bad) == []
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Roper break-action source or browser schema regressed.")
        raise


def test_held_target_and_adjacent_ally_can_break_tendril_without_moving_owner():
    try:
        source, attack, rule, held, helper, owner, setup = _fixture()
        apply_hit_conditions(attack, held.state, "owner", setup=setup)
        assert held.state.grapple_sources[0].linked_effect_id == attack.id
        assert eligible(held, held, owner, rule)
        assert eligible(helper, held, owner, rule)
        assert choose_grapple_helper_rescue(helper, setup) is not None
        helper.position_ft = 55
        assert not eligible(helper, held, owner, rule)
        helper.position_ft = 45
        break_event = resolve_grapple_helper_rescue(
            1, 1, helper, held, owner, rule, FixedDiceProvider([20]), setup,
        )
        assert break_event.check_succeeded
        assert break_event.check_dc == 15
        assert break_event.feature_id == attack.id
        assert "Tendril" in break_event.description
        assert "break" in break_event.description
        assert not helper.state.action_available
        assert held.state.grapple_sources == []
        assert "grappled" not in held.state.active_effect_ids
        assert "restrained" not in held.state.active_effect_ids
        assert owner.state.current_hp == owner.state.template.max_hp
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 1

        apply_hit_conditions(attack, held.state, "owner", setup=setup)
        # The held target's own Strength check is subject to its actual
        # printed source-owned disadvantage, as the generic check stack decides.
        self_break = resolve_grapple_helper_rescue(
            2, 2, held, held, owner, rule, FixedDiceProvider([20, 20]), setup,
        )
        assert self_break.check_succeeded
        assert not held.state.action_available
        assert not held.state.grapple_sources
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 2
        begin_turn(owner.state)
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 0
    except Exception:
        logger.exception("Universal held/third-party break Action did not release Tendril.")
        raise
