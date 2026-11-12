"""2014 Command must be castable from source data into real fight state.

This integrates the printed 2014 Androsphinx, Commoner, generic spell
selection eligibility, spell slot use, and failed-save turn marker.
"""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.spell_choice import SpellChoice
from app.combat.spell_policy_targeting import legal_single_spell_targets
from app.combat.spell_resolution import resolve_spell
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import (
    adapt_basic_monster_2014, adapt_monster_mechanics_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_printed_androsphinx_command_grovel_targets_commoner_through_existing_engine() -> None:
    try:
        source = {row.id: row for row in load_monster_source_2014()}
        original = {name: source[name].model_dump_json() for name in ("androsphinx", "commoner")}
        caster_template = compile_combatant(adapt_monster_mechanics_2014(source["androsphinx"]))
        target_template = compile_combatant(adapt_basic_monster_2014(source["commoner"]))
        assert "common" in caster_template.language_profile.spoken
        assert "common" in target_template.language_profile.understood
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=20,
            state=build_combatant_state(caster_template),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(target_template),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[caster], ruleset="2014",
            hero_total_levels=1, monster_total_cr=source["androsphinx"].challenge_rating,
        )
        spell = next(action for action in caster_template.spell_save_actions
                     if action.id == "command")
        assert legal_single_spell_targets(caster, setup, spell) == [target]
        begin_turn(caster.state)
        slot = next(item for item in caster.state.resources if item.id == "spell-slot-1")
        remaining_before = slot.current_uses
        assert remaining_before > 0
        choice = SpellChoice(action=spell, slot_level=1, target_ids=("target",))
        events, sequence = resolve_spell(
            1, 1, caster, setup, choice, "1:caster", FixedDiceProvider([1]),
        )
        assert sequence > 1
        assert slot.current_uses == remaining_before - 1
        assert not caster.state.action_available
        assert any(event.feature_id == "command" and "Command" in event.description
                   for event in events)
        assert "commanded" in target.state.active_effect_ids
        assert "prone" not in target.state.active_effect_ids
        assert any(effect.effect_id == "commanded"
                   and effect.expires_target_turn_count == 1
                   for effect in target.state.timed_effects)
        assert {name: source[name].model_dump_json() for name in original} == original
    except Exception:
        logger.exception("Printed Androsphinx Command did not cast through generic spell engine.")
        raise
