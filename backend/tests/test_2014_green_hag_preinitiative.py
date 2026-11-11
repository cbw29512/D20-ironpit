"""Green Hag: one pre-initiative Invisible buff, then normal melee or spell AI."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.pit_policy import choose_standard_attack
from app.combat.precombat_buffs import choose_opening_buff, prepare_opening_buffs
from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _fight(distance_ft: int):
    """Construct both combatants through the ordinary source-to-template path."""
    try:
        cards = {row.id: row for row in load_monster_source_2014()}
        hag = EncounterCombatant(
            combatant_id="green-hag", side="monsters", position_ft=0,
            state=build_combatant_state(compile_combatant(
                adapt_basic_monster_2014(cards["green-hag"]),
            )),
        )
        enemy = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=distance_ft,
            state=build_combatant_state(compile_combatant(
                adapt_basic_monster_2014(cards["commoner"]),
            )),
        )
        setup = EncounterSetup(
            heroes=[enemy], monsters=[hag], ruleset="2014",
            hero_total_levels=1, monster_total_cr="3",
        )
        return hag, enemy, setup
    except Exception:
        logger.exception("Could not build actual 2014 Green Hag combat setup.")
        raise


def test_invisible_passage_is_the_single_free_preinitiative_buff():
    try:
        hag, enemy, setup = _fight(30)
        assert hag.state.opening_buff_id is None
        assert hag.state.initiative_roll is None
        choice = choose_opening_buff(hag, setup)
        assert choice is not None and choice.kind == "timed-self-buff"
        assert choice.timed_action is not None
        assert choice.timed_action.name == "Invisible Passage"

        events, sequence = prepare_opening_buffs(setup)
        assert len(events) == 1 and sequence == 2
        assert events[0].round_number == 0
        assert events[0].actor_id == "green-hag"
        assert events[0].feature_id == "invisible-passage"
        assert "Precombat preparation" in events[0].description
        assert hag.state.opening_buff_id == "invisible-passage"
        assert "invisible" in hag.state.active_effect_ids
        # The browser receives the same typed buff and does not need a hag-specific pre-fight resolver.
        row = next(item for item in template_row(hag.state.template)["timed_self_buff_actions"]
                   if item["id"] == "invisible-passage")
        assert row["name"] == "Invisible Passage"
        assert row.get("openingEligible", True) is True
        assert row["conditionIds"] == ["invisible"]
        assert row["endsOnOwnerAttack"] and row["endsOnOwnerSpellCast"]
        assert hag.state.concentration is not None
        assert hag.state.concentration.effect_id == "invisible-passage"
        # A preparation choice costs no first-turn Action, Bonus Action or Reaction.
        assert hag.state.action_available
        assert hag.state.bonus_action_available
        assert hag.state.reaction_available

        second, same_sequence = prepare_opening_buffs(setup, sequence)
        assert second == [] and same_sequence == sequence
        initiative = roll_encounter_initiative(setup, FixedDiceProvider([12, 18]))
        assert "green-hag" in initiative.turn_order
        assert hag.state.initiative_roll is not None
        assert "invisible" in hag.state.active_effect_ids
    except Exception:
        logger.exception("Green Hag pre-initiative Invisibility regression failed.")
        raise


def test_source_claws_are_melee_and_vicious_mockery_is_ranged_offense():
    try:
        close, close_target, close_setup = _fight(5)
        close_attack = choose_standard_attack(close, close_setup)
        assert close_attack is not None
        assert close_attack[1].weapon.name == "Claws"
        assert close_attack[1].weapon.attack_kind.value == "melee"
        assert close_attack[2] <= 5

        far, far_target, far_setup = _fight(30)
        assert choose_standard_attack(far, far_setup) is None
        ranged = choose_spell(far, far_setup, "1:green-hag")
        assert ranged is not None and ranged.action.id == "vicious-mockery"
        assert ranged.action.range_ft == 60
        assert ranged.action.dc == 12
        assert ranged.action.damage_type == "psychic"
        assert ranged.target_ids == ("target",)
    except Exception:
        logger.exception("Green Hag melee/ranged attack selection regression failed.")
        raise


def test_melee_and_spellcasting_each_end_the_same_precombat_invisibility():
    try:
        for event_type, distance in (("attack", 5), ("spell_cast", 30)):
            hag, _, setup = _fight(distance)
            prepare_opening_buffs(setup)
            assert "invisible" in hag.state.active_effect_ids
            ended = expire_on_owner_event(hag.state, event_type, [hag.state])
            assert ended == ["invisible"]
            assert hag.state.concentration is None
            assert hag.state.opening_buff_id == "invisible-passage"
            assert "invisible" not in hag.state.active_effect_ids
            # Pre-fight one-use allowance cannot be repeated after breaking it.
            assert choose_opening_buff(hag, setup) is None
    except Exception:
        logger.exception("Generic Green Hag Invisibility owner-exit regression failed.")
        raise
