"""Roper Tendril durability reuses universal source-owned Grapple objects.

Admission stays blocked until direct attacks against appendages, helper
Strength breaks, and next-turn replacement behavior are certified.
"""
from __future__ import annotations

import logging

from app.combat.breakable_grapple_object import damage_breakable_grapple_object
from app.combat.grapple_appendage_capacity import source_grapple_capacity_used
from app.combat.state import begin_turn
from app.combat.conditions import apply_hit_conditions
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _fixture():
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "roper")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        attack = next(x for x in [template.weapon_attack, *template.alternate_weapon_attacks]
                      if x and x.id == "2014-roper-tendril")
        source = EncounterCombatant(combatant_id="owner", side="monsters",
                                   position_ft=0, state=build_combatant_state(template))
        victim = EncounterCombatant(combatant_id="victim", side="heroes",
                                   position_ft=5, state=build_combatant_state(build_commoner()))
        setup = EncounterSetup(heroes=[victim], monsters=[source],
                               ruleset="2014", hero_total_levels=1, monster_total_cr="5")
        return card, template, attack, victim, setup
    except Exception:
        logger.exception("Failed to prepare source-neutral Roper Grapple fixture.")
        raise


def test_printed_tendril_durability_compiles_and_is_fight_local():
    try:
        card, template, attack, victim, setup = _fixture()
        old = card.model_dump_json()
        spec = attack.control_effect.grapple_breakable_object
        assert spec is not None
        assert (spec.armor_class, spec.hit_points) == (20, 10)
        assert {x.value for x in spec.damage_immunities} == {"poison", "psychic"}
        assert attack.control_effect.grapple_escape_dc == 15
        assert attack.control_effect.grapple_max_active_grapples == 6
        exported = template_row(template)
        row = next(x for x in exported["attacks"] if x["id"] == attack.id)
        assert row["controlEffect"]["grappleBreakableObject"] == {
            "armorClass": 20, "hitPoints": 10,
            "damageImmunities": ["poison", "psychic"], "damageVulnerabilities": [],
        }
        hp_before = victim.state.current_hp
        assert apply_hit_conditions(attack, victim.state, "owner", setup=setup) == [
            "grappled", "restrained",
        ]
        grapple = victim.state.grapple_sources[0]
        assert grapple.breakable_object.current_hp == 10
        assert "source:trait" in basic_blockers_2014(card)
        assert "source:extra-action" in basic_blockers_2014(card)
        assert card.model_dump_json() == old
        assert victim.state.current_hp == hp_before
    except Exception:
        logger.exception("Printed Roper durability failed universal binding.")
        raise


def test_tendril_object_hits_are_not_hits_against_owner_and_end_its_grapple():
    try:
        _, _, attack, victim, setup = _fixture()
        apply_hit_conditions(attack, victim.state, "owner", setup=setup)
        original_hp = victim.state.current_hp
        grapple = victim.state.grapple_sources[0]
        assert damage_breakable_grapple_object(victim.state, grapple, 19, 4, "slashing", setup) == (0, False)
        assert damage_breakable_grapple_object(victim.state, grapple, 20, 99, "poison", setup) == (0, False)
        assert damage_breakable_grapple_object(victim.state, grapple, 21, 99, "psychic", setup) == (0, False)
        assert grapple.breakable_object.current_hp == 10
        assert damage_breakable_grapple_object(victim.state, grapple, 22, 4, "slashing", setup) == (4, False)
        assert grapple.breakable_object.current_hp == 6
        assert damage_breakable_grapple_object(victim.state, grapple, 22, 6, "piercing", setup) == (6, True)
        assert victim.state.grapple_sources == []
        assert "grappled" not in victim.state.active_effect_ids
        assert "restrained" not in victim.state.active_effect_ids
        assert victim.state.current_hp == original_hp
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 1
        assert setup.monsters[0].state.broken_grapple_appendages[attack.id] == 1
        begin_turn(setup.monsters[0].state)
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 0
        assert damage_breakable_grapple_object.__name__ == "damage_breakable_grapple_object"
    except Exception:
        logger.exception("Breakable Grapple target state failed universal damage/release rules.")
        raise



def test_six_source_slots_do_not_reappear_until_next_owner_turn():
    try:
        _, _, attack, first, setup = _fixture()
        apply_hit_conditions(attack, first.state, "owner", setup=setup)
        grapple = first.state.grapple_sources[0]
        assert damage_breakable_grapple_object(
            first.state, grapple, 20, 10, "slashing", setup,
        ) == (10, True)
        held = []
        for index in range(5):
            member = EncounterCombatant(
                combatant_id=f"held-{index}", side="heroes", position_ft=5,
                state=build_combatant_state(build_commoner()),
            )
            setup.heroes.append(member)
            held.append(member)
            assert apply_hit_conditions(attack, member.state, "owner", setup=setup) == [
                "grappled", "restrained",
            ]
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 6
        sixth = EncounterCombatant(
            combatant_id="sixth", side="heroes", position_ft=5,
            state=build_combatant_state(build_commoner()),
        )
        setup.heroes.append(sixth)
        assert apply_hit_conditions(attack, sixth.state, "owner", setup=setup) == []
        assert sixth.state.grapple_sources == []
        begin_turn(setup.monsters[0].state)
        assert source_grapple_capacity_used(setup, "owner", attack.id) == 5
        assert apply_hit_conditions(attack, sixth.state, "owner", setup=setup) == [
            "grappled", "restrained",
        ]
    except Exception:
        logger.exception("Broken tendrils violated next-owner-turn replacement capacity.")
        raise
