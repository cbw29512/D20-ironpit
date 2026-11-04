"""Terminal encounter snapshots must not retain source-target links to defeated combatants."""
from __future__ import annotations

from app.combat.attachments import attach
from app.combat.dice import SeededDiceProvider
from app.combat.encounter_events import build_encounter_result
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.domain.attachments import Attachment
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    hero = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    source = EncounterCombatant(
        combatant_id="source", side="monsters", position_ft=0,
        state=build_combatant_state(build_commoner()),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[source], hero_total_levels=1,
        monster_total_cr="1/8", ruleset="2014",
    )
    setup.attachments = list(attach((), Attachment(
        source_id="source", target_id="victim", effect_id="linked",
        source_name="Named Drain", damage_dice_count=1, damage_dice_size=4,
        damage_bonus=3, periodic_effect_kind="direct_hp_loss", damage_type=None,
    )))
    return setup, source, hero


def test_final_result_clears_link_when_target_dies_without_next_turn():
    setup, source, target = _setup()
    initiative = roll_encounter_initiative(setup, SeededDiceProvider(4321))
    target.state.is_dead = True
    target.state.is_alive = False
    result = build_encounter_result(setup, initiative, [], "monsters_win", 2)
    assert result.setup.attachments == []
    assert source.state.is_alive


def test_final_result_clears_link_when_source_dies_without_next_turn():
    setup, source, target = _setup()
    initiative = roll_encounter_initiative(setup, SeededDiceProvider(4321))
    source.state.is_dead = True
    source.state.is_alive = False
    result = build_encounter_result(setup, initiative, [], "heroes_win", 2)
    assert result.setup.attachments == []
    assert target.state.is_alive


def test_active_final_link_is_not_deleted_solely_because_fight_stopped():
    setup, source, target = _setup()
    initiative = roll_encounter_initiative(setup, SeededDiceProvider(4321))
    result = build_encounter_result(setup, initiative, [], "draw", 100)
    assert len(result.setup.attachments) == 1
    assert result.setup.attachments[0].source_name == "Named Drain"
