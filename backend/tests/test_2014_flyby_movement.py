from __future__ import annotations

import logging

from app.combat.opportunity_attack_rules import opportunity_attack_weapon
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)
_EXPECTED_FLYBY = {"Flying Snake", "Giant Owl", "Owl", "Pteranodon"}


def _flyby_templates():
    try:
        sources = [monster for monster in load_monster_source_2014() if "Flyby" in monster.trait_names]
        assert {monster.name for monster in sources} == _EXPECTED_FLYBY
        return [compile_combatant(adapt_basic_monster_2014(monster)) for monster in sources]
    except Exception:
        logger.exception("Failed to build 2014 Flyby fixtures.")
        raise


def test_2014_flyby_monsters_use_horizontal_fly_speed() -> None:
    try:
        for template in _flyby_templates():
            assert template.movement_modes.fly_ft > 0
            assert template.speed_ft == max(template.movement_modes.walk_ft, template.movement_modes.fly_ft)
            assert template.opportunity_attack_exempt_movement_modes == ["fly"]

            state = build_combatant_state(template)
            begin_turn(state)

            assert state.movement_mode == "fly"
            assert state.movement_remaining_ft == template.movement_modes.fly_ft
    except Exception:
        logger.exception("2014 horizontal Fly speed regression failed.")
        raise


def test_flyby_oa_exemption_is_qualified_to_flight_mode() -> None:
    try:
        owl = next(template for template in _flyby_templates() if template.name == "Giant Owl")
        mover = EncounterCombatant(
            combatant_id="owl",
            side="monsters",
            position_ft=5,
            state=build_combatant_state(owl),
        )
        reactor = EncounterCombatant(
            combatant_id="fighter",
            side="heroes",
            position_ft=0,
            state=build_combatant_state(build_karnok_stoneward_2014(5)),
        )
        begin_turn(mover.state)

        assert mover.state.movement_mode == "fly"
        assert opportunity_attack_weapon(reactor, mover, 5, 10, "speed") is None
        assert reactor.state.reaction_available is True

        mover.state.movement_mode = "walk"
        attack = opportunity_attack_weapon(reactor, mover, 5, 10, "speed")
        assert attack is not None
    except Exception:
        logger.exception("2014 Flyby mode-qualified OA regression failed.")
        raise
