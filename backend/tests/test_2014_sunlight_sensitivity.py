from __future__ import annotations

import logging

from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.environment_contexts import (
    actor_inside_environment_context,
    environment_context_disadvantage_sources,
)
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.environment_context_reactions import sunlight_sensitivity_2014
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)

_SUNLIGHT_SENSITIVE_IDS = (
    "drider", "drow", "duergar", "kobold", "specter", "wight", "wraith",
)


def _source():
    try:
        return {monster.id: monster for monster in load_monster_source_2014()}
    except Exception:
        logger.exception("Failed to load 2014 monster source for Sunlight Sensitivity tests.")
        raise


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed to build encounter member %s.", combatant_id)
        raise


def _kobold(position: int = 5) -> EncounterCombatant:
    try:
        monster = _source()["kobold"]
        return _member(compile_combatant(adapt_basic_monster_2014(monster)), "kobold", "monsters", position)
    except Exception:
        logger.exception("Failed to compile the 2014 Kobold.")
        raise


def _setup(kobold_position: int = 5):
    try:
        paladin = _member(build_aurelia_brightshield_2014(20), "aurelia", "heroes", 0)
        kobold = _kobold(kobold_position)
        setup = EncounterSetup(
            heroes=[paladin], monsters=[kobold], hero_total_levels=20, monster_total_cr="1/8", ruleset="2014",
        )
        return setup, paladin, kobold
    except Exception:
        logger.exception("Failed to build Holy Nimbus / Kobold sunlight setup.")
        raise


def _activate(paladin: EncounterCombatant) -> None:
    try:
        begin_turn(paladin.state)
        action = paladin.state.template.timed_self_buff_actions[0]
        event = resolve_timed_self_buff(1, 1, paladin, action)
        assert event.feature_id == "holy-nimbus"
    except Exception:
        logger.exception("Failed to activate 2014 Holy Nimbus.")
        raise


def test_sunlight_sensitivity_is_bound_not_arena_neutral() -> None:
    try:
        source = _source()
        reaction = sunlight_sensitivity_2014()
        for monster_id in _SUNLIGHT_SENSITIVE_IDS:
            monster = source[monster_id]
            assert "Sunlight Sensitivity" in monster.trait_names
            assert "Sunlight Sensitivity" not in ARENA_NEUTRAL_TRAITS_2014
            assert "Sunlight Sensitivity" in bound_trait_names_2014(monster)
            assert "Sunlight Sensitivity" not in unsupported_traits_2014(monster)
            if basic_blockers_2014(monster):
                continue
            template = compile_combatant(adapt_basic_monster_2014(monster))
            assert template.environment_context_reactions == [reaction]
            if monster_id == "kobold":
                assert CombatTrait.PACK_TACTICS in template.combat_traits
    except Exception:
        logger.exception("2014 Sunlight Sensitivity source-binding regression failed.")
        raise


def test_kobold_takes_holy_nimbus_sunlight_disadvantage() -> None:
    try:
        setup, paladin, kobold = _setup()
        _activate(paladin)
        assert actor_inside_environment_context(kobold, setup, "sunlight") is True
        assert environment_context_disadvantage_sources(kobold, setup, "attack_rolls") == 1
        begin_turn(kobold.state)
        event = resolve_encounter_attack(
            2, 1, kobold, paladin, kobold.state.template.weapon_attack, 5,
            FixedDiceProvider([3, 17, 4]), setup,
        )
        assert event.attack_roll is not None
        assert event.attack_roll.mode is RollMode.DISADVANTAGE
        assert event.attack_roll.selected_roll == 3
    except Exception:
        logger.exception("2014 Kobold Holy Nimbus sunlight reaction regression failed.")
        raise


def test_kobold_has_no_penalty_outside_live_sunlight() -> None:
    try:
        setup, paladin, kobold = _setup(kobold_position=35)
        _activate(paladin)
        assert actor_inside_environment_context(kobold, setup, "sunlight") is False
        assert environment_context_disadvantage_sources(kobold, setup, "attack_rolls") == 0
        idle_paladin = _member(build_aurelia_brightshield_2014(20), "idle", "heroes", 0)
        unused = _kobold()
        idle_setup = EncounterSetup(
            heroes=[idle_paladin], monsters=[unused], hero_total_levels=20, monster_total_cr="1/8", ruleset="2014",
        )
        assert environment_context_disadvantage_sources(unused, idle_setup, "attack_rolls") == 0
    except Exception:
        logger.exception("2014 Kobold sunlight-absent regression failed.")
        raise
