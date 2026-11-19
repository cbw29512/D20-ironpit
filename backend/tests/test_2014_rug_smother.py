"""2014 Smother uses one source-semantic universal grapple lifecycle."""
from __future__ import annotations

from app.combat.grapple_periodic_damage import grapple_turn_start_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_smother_2014 import source_proven_smother_attacks_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.content.monsters import build_commoner
from scripts.browser_template_serializer import template_row


def _catalog():
    cards = load_monster_source_2014()
    assert len(cards) == 327
    return cards


def test_exact_source_scan_binds_only_printed_smother_parameters():
    matches = [(card, source_proven_smother_attacks_2014(card)) for card in _catalog()]
    matches = [(card, actions) for card, actions in matches if actions]
    assert len(matches) == 1
    card, (definition,) = matches[0]
    assert card.id == "rug-of-smothering"
    assert basic_blockers_2014(card) == ()
    template = compile_combatant(adapt_basic_monster_2014(card))
    attack = template.weapon_attack
    assert (attack.attack_bonus, attack.weapon.reach_ft, attack.fixed_damage) == (5, 5, 0)
    control = attack.control_effect
    assert (control.grapple_escape_dc, control.max_target_size.value) == (13, "medium")
    assert control.restrains_while_grappled and control.grapple_blinds
    assert control.grapple_prevents_breathing and control.grapple_requires_source_free
    periodic = control.grapple_periodic_damage
    assert (periodic.dice_count, periodic.dice_size, periodic.damage_bonus, periodic.damage_type) == (2, 6, 3, "bludgeoning")
    browser = template_row(template)["attacks"][0]["controlEffect"]
    assert browser["grappleBlinds"] and browser["grapplePreventsBreathing"]
    assert browser["grapplePeriodicDamage"]["damage_bonus"] == 3


def test_periodic_bonus_uses_existing_owner_linked_turn_tick():
    card = next(card for card in _catalog() if card.id == "rug-of-smothering")
    rug = EncounterCombatant(
        combatant_id="rug", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(adapt_basic_monster_2014(card))),
    )
    victim = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    attack = rug.state.template.weapon_attack
    from app.combat.conditions import apply_hit_conditions
    setup = EncounterSetup(heroes=[victim], monsters=[rug], ruleset="2014", hero_total_levels=1, monster_total_cr="2")
    assert set(apply_hit_conditions(attack, victim.state, "rug", source_template=rug.state.template, setup=setup)) == {"grappled", "restrained"}
    assert "blinded" in victim.state.active_effect_ids
    assert victim.state.grapple_sources[0].prevents_breathing
    packet, = grapple_turn_start_damage(victim, setup, type("Dice", (), {"roll": lambda self, sides: 2})())
    assert packet == ("Smother", 7, "bludgeoning", "rug")
