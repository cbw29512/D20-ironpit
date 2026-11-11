"""Grapple-linked check/save modifiers reuse the universal d20 pipelines."""
from __future__ import annotations

import logging

from app.combat.conditions import apply_hit_conditions
from app.combat.exhaustion import ability_check_disadvantage_sources
from app.combat.grapple import release_grapple
from app.combat.grapple_check_save_disadvantage import grapple_check_save_disadvantage_sources
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import RollMode

logger = logging.getLogger(__name__)


def test_roper_tendril_grapple_penalty_follows_existing_state_lifecycle():
    try:
        roper = next(card for card in load_monster_source_2014() if card.id == "roper")
        template = adapt_monster_mechanics_2014(roper)
        attack = compile_attack(next(a for a in template.attacks if a.name == "Tendril"))
        assert attack.control_effect.grapple_check_save_disadvantage_abilities == ["strength"]
        victim = build_combatant_state(build_commoner())
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=5,
            state=build_combatant_state(build_commoner()),
        )
        target = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=5, state=victim,
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[owner], hero_total_levels=1,
            monster_total_cr="1", ruleset="2014",
        )
        assert grapple_check_save_disadvantage_sources(victim, "strength") == 0
        assert apply_hit_conditions(attack, victim, "owner", setup=setup) == [
            "grappled", "restrained",
        ]
        assert grapple_check_save_disadvantage_sources(victim, "strength") == 1
        assert grapple_check_save_disadvantage_sources(victim, "dexterity") == 0
        assert ability_check_disadvantage_sources(victim, "strength") == 1
        assert saving_throw_mode(victim, "strength") is RollMode.DISADVANTAGE
        assert attack.control_effect.grapple_check_save_disadvantage_abilities == ["strength"]
        release_grapple(victim, "owner")
        assert grapple_check_save_disadvantage_sources(victim, "strength") == 0
        assert ability_check_disadvantage_sources(victim, "strength") == 0
        assert saving_throw_mode(victim, "strength") is RollMode.NORMAL
    except Exception:
        logger.exception("Source-neutral linked grapple disadvantage lifecycle failed")
        raise


def test_grapple_penalty_is_not_ordinary_strength_attack_disadvantage():
    try:
        roper = next(card for card in load_monster_source_2014() if card.id == "roper")
        attack = compile_attack(next(
            a for a in adapt_monster_mechanics_2014(roper).attacks if a.name == "Tendril"
        ))
        assert attack.control_effect.grapple_check_save_disadvantage_abilities == ["strength"]
        assert "strength" not in attack.conditional_attack_advantage
    except Exception:
        logger.exception("Grapple check/save modifier leaked into attack modifier")
        raise
