"""Pinned 2014 attack and generic attachment receipts through live combat paths."""
import pytest

from app.combat.attacks import resolve_attack
from app.combat.attachment_decision import resolve_attachment_removal_action
from app.combat.attachment_on_hit import apply_attack_hit_attachment
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _combat():
    card = next(row for row in load_monster_source_2014() if row.id == "stirge")
    attack = compile_attack(_attack(card, card.attacks[0]))
    attacker = EncounterCombatant(
        combatant_id="stirge", side="monsters", position_ft=0,
        state=build_combatant_state(build_commoner()),
    )
    victim_template = build_commoner().model_copy(update={"max_hp": 50})
    target = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=5,
        state=build_combatant_state(victim_template),
    )
    target.state.current_hp = 50
    target.state.temporary_hp = 8
    setup = EncounterSetup(
        heroes=[target], monsters=[attacker], hero_total_levels=1,
        monster_total_cr="1/8", ruleset="2014",
    )
    return attack, attacker, target, setup


def test_real_successful_attack_creates_link_and_blocks_second_attack():
    attack, attacker, victim, setup = _combat()
    event = resolve_attack(
        1, 1, attacker.state, victim.state, attack, 5, FixedDiceProvider([18, 2]),
        actor_event_id=attacker.combatant_id, target_event_id=victim.combatant_id,
        spend_action=False, reaction_setup=setup, reaction_roller=attacker,
        affected_states=[attacker.state, victim.state],
    )
    assert event.hit is True
    assert (event.hp_before, event.hp_after) == (50, 50)
    assert victim.state.temporary_hp == 3
    assert victim.state.grapple_sources == []
    assert len(setup.attachments) == 1
    assert len(event.attachment_changes) == 1
    assert event.attachment_changes[0].operation == "attach"
    assert event.attachment_changes[0].source_name == "Blood Drain"
    with pytest.raises(ValueError, match="attachment prevents another attack"):
        resolve_attack(
            2, 1, attacker.state, victim.state, attack, 5, FixedDiceProvider([1]),
            actor_event_id=attacker.combatant_id, target_event_id=victim.combatant_id,
            spend_action=False, reaction_setup=setup,
        )


def test_generic_removal_action_reports_detach_receipt_and_spends_action():
    attack, attacker, victim, setup = _combat()
    assert apply_attack_hit_attachment(
        attack, attacker.combatant_id, victim.combatant_id, victim.state, setup,
    )
    event = resolve_attachment_removal_action(1, 2, victim, setup)
    assert event is not None and event.feature_id == "Blood Drain"
    assert not victim.state.action_available
    assert [(change.operation, change.source_name) for change in event.attachment_changes] == [
        ("detach", "Blood Drain"),
    ]
    assert setup.attachments == []
