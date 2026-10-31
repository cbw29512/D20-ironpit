"""Card-neutral two/ten-target grappling limits in 327 pinned 2014 sources."""
from __future__ import annotations

from app.combat.conditions import apply_hit_conditions
from app.combat.grapple import release_grapple
from app.combat.grapple_queries import source_grapple_count
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_grapple_capacity_2014 import (
    source_completed_limited_grapple_2014,
)
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup

EXPECTED = {
    "giant-crab": (2, False),
    "giant-scorpion": (2, False),
    "glabrezu": (2, False),
    "kraken": (10, True),
    "otyugh": (2, True),
}


def _encounter():
    def member(identifier, side):
        return EncounterCombatant(
            combatant_id=identifier, side=side, position_ft=5,
            state=build_combatant_state(build_commoner()),
        )
    attacker = member("source", "monsters")
    targets = [member(f"target-{n}", "heroes") for n in range(3)]
    setup = EncounterSetup(
        heroes=targets, monsters=[attacker], hero_total_levels=3,
        monster_total_cr="2", ruleset="2014",
    )
    return attacker, targets, setup


def test_327_source_scan_only_accepts_complete_printed_appendage_limits():
    cards = load_monster_source_2014()
    assert len(cards) == 327
    found = {}
    for card in cards:
        for attack in card.attacks:
            result = source_completed_limited_grapple_2014(card, attack)
            limit = (result.control_effect or {}).get("max_active_grapples")
            if limit is not None:
                found[card.id] = (limit, result.control_effect.get("restrains_while_grappled", False))
    assert found == EXPECTED


def test_every_source_grapple_capacity_compiles_in_existing_weapon_control():
    cards = {card.id: card for card in load_monster_source_2014()}
    for identifier, (limit, restrains) in EXPECTED.items():
        card = cards[identifier]
        original = card.model_dump_json()
        source = next(row for row in card.attacks if
                      source_completed_limited_grapple_2014(card, row).control_effect
                      and source_completed_limited_grapple_2014(
                          card, row).control_effect.get("max_active_grapples"))
        weapon = compile_attack(_attack(card, source))
        assert weapon.control_effect.grapple_max_active_grapples == limit
        assert weapon.control_effect.restrains_while_grappled == restrains
        assert card.model_dump_json() == original


def test_unrecognized_clause_and_unknown_source_changes_remain_blocked():
    card = next(row for row in load_monster_source_2014() if row.id == "otyugh")
    attack = card.attacks[1]
    changed = card.model_copy(update={
        "source_actions": (card.source_actions or "").replace(
            "two tentacles", "three tentacles",
        ),
    })
    assert source_completed_limited_grapple_2014(
        changed, attack,
    ).source_complete is False
    changed = card.model_copy(update={
        "source_actions": (card.source_actions or "").replace(
            "restrained until the grapple ends",
            "restrained and stunned until the grapple ends",
        ),
    })
    assert source_completed_limited_grapple_2014(
        changed, attack,
    ).source_complete is False


def test_generic_two_target_grapple_and_release_reset_for_fresh_target():
    card = next(row for row in load_monster_source_2014() if row.id == "otyugh")
    attack = compile_attack(_attack(card, card.attacks[1]))
    source, targets, setup = _encounter()
    for target in targets[:2]:
        assert apply_hit_conditions(
            attack, target.state, source.combatant_id, setup=setup,
        ) == ["grappled", "restrained"]
    assert source_grapple_count(setup, source.combatant_id) == 2
    assert apply_hit_conditions(
        attack, targets[2].state, source.combatant_id, setup=setup,
    ) == []
    assert targets[2].state.grapple_sources == []
    release_grapple(targets[0].state, source.combatant_id)
    assert source_grapple_count(setup, source.combatant_id) == 1
    assert apply_hit_conditions(
        attack, targets[2].state, source.combatant_id, setup=setup,
    ) == ["grappled", "restrained"]
    assert source_grapple_count(setup, source.combatant_id) == 2
