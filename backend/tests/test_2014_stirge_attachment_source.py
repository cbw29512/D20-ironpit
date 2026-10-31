"""A real pinned 2014 card binds generic attachment, not a Stirge-specific resolver."""
from __future__ import annotations

from app.combat.attachment_on_hit import apply_attack_hit_attachment
from app.combat.attachment_attack_gate import source_attacks_blocked
from app.combat.attachment_removal import remove_attachment_by_action, detach_attachment_with_movement
from app.combat.attachment_turn_events import resolve_attachment_turn_start_events
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_attachment_2014 import supports_source_attachment_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _card():
    return next(row for row in load_monster_source_2014() if row.id == "stirge")


def _combat():
    card = _card()
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
    return card, attack, attacker, target, setup


def test_source_card_produces_typed_free_link_and_retains_source_parameters():
    card, attack, *_ = _combat()
    original = card.model_dump_json()
    assert supports_source_attachment_2014(card.attacks[0])
    effects = basic_attack_effects_2014(card.attacks[0])
    assert any(effect.kind == "attachment" for effect in effects)
    assert attack.attack_bonus == 5
    assert attack.weapon.dice_count == 1 and attack.weapon.dice_size == 4
    assert attack.damage_bonus == 3
    spec = attack.on_hit_attachment
    assert spec.source_name == "Blood Drain"
    assert spec.periodic_effect_kind == "direct_hp_loss"
    assert spec.damage_type is None
    assert (spec.dice_count, spec.dice_size, spec.damage_bonus) == (1, 4, 3)
    assert (spec.auto_end_after_hp_loss, spec.source_detach_movement_ft) == (10, 5)
    assert spec.blocks_source_attacks and spec.action_removable
    assert card.model_dump_json() == original


def test_malformed_source_stays_unclassified():
    card = _card()
    original = card.attacks[0]
    tampered = original.model_copy(update={"ongoing_damage_effect": {
        **original.ongoing_damage_effect, "made_up_grapple_dc": 11,
    }})
    assert not supports_source_attachment_2014(tampered)
    tampered = original.model_copy(update={"ongoing_damage_effect": {
        **original.ongoing_damage_effect, "tick_timing": "target_turn_start",
    }})
    assert not supports_source_attachment_2014(tampered)


def test_source_declaration_makes_link_tick_once_and_detach_after_ten_actual_loss():
    _, attack, attacker, victim, setup = _combat()
    assert apply_attack_hit_attachment(
        attack, attacker.combatant_id, victim.combatant_id, victim.state, setup,
    )
    assert len(setup.attachments) == 1
    assert victim.state.active_effect_ids == []
    events, seq = resolve_attachment_turn_start_events(
        1, 1, attacker, setup, FixedDiceProvider([1]),
    )
    assert seq == 2
    assert (victim.state.current_hp, victim.state.temporary_hp) == (46, 8)
    assert events[0].feature_id == "Blood Drain"
    assert setup.attachments[0].actual_hp_lost == 4
    events, seq = resolve_attachment_turn_start_events(
        seq, 2, attacker, setup, FixedDiceProvider([4]),
    )
    assert seq == 3
    assert victim.state.current_hp == 39
    assert setup.attachments == []


def test_renamed_id_still_compiles_source_neutral_effect():
    card = _card()
    source = card.attacks[0]
    renamed = source.model_copy(update={
        "id": "renamed-source", "name": "Custom Needle",
        "ongoing_damage_effect": {**source.ongoing_damage_effect, "name": "Custom Needle"},
    })
    assert supports_source_attachment_2014(renamed)
    effects = basic_attack_effects_2014(renamed)
    compiled = next(effect for effect in effects if effect.kind == "attachment")
    assert compiled.source_name == "Custom Needle"


def test_target_can_use_action_and_source_can_spend_movement_to_detach():
    _, attack, attacker, victim, setup = _combat()
    assert apply_attack_hit_attachment(
        attack, attacker.combatant_id, victim.combatant_id, victim.state, setup,
    )
    assert source_attacks_blocked(setup, attacker.combatant_id)
    victim.position_ft = 5
    attacker.position_ft = 0
    assert remove_attachment_by_action(
        setup, victim, attacker.combatant_id, "attached-blood-drain",
    )
    assert not victim.state.action_available
    assert not source_attacks_blocked(setup, attacker.combatant_id)
    setup.attachments.clear()
    assert apply_attack_hit_attachment(
        attack, attacker.combatant_id, victim.combatant_id, victim.state, setup,
    )
    attacker.state.movement_remaining_ft = 10
    assert detach_attachment_with_movement(setup, attacker, "attached-blood-drain")
    assert attacker.state.movement_remaining_ft == 5
    assert setup.attachments == []



def test_pinned_stirge_enters_generic_2014_roster_without_special_mechanics():
    card = _card()
    assert basic_blockers_2014(card) == ()
    cards = [row for row in build_basic_2014_monsters() if row.id == "2014-stirge"]
    assert len(cards) == 1
    assert cards[0].max_hp == 2
    assert cards[0].armor_class == 14
