"""Actual source cards and positioned combatants for visible-ally parity tests."""
import logging

from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


def source(monster_id="bearded-devil"):
    try:
        return next(item for item in load_monster_source_2014() if item.id == monster_id)
    except Exception:
        logger.exception("Failed to load test source %s.", monster_id)
        raise


def template(monster_id="bearded-devil"):
    try:
        return compile_combatant(adapt_basic_monster_2014(source(monster_id)))
    except Exception:
        logger.exception("Failed to compile test source %s.", monster_id)
        raise


def setup_with_card(card=None):
    try:
        members = []
        for name, side, x, card in (
            ("owner", "monsters", 1, card or template()),
            ("ally", "monsters", 7, template("commoner")),
            ("foe", "heroes", 2, template("adult-black-dragon")),
        ):
            state = build_combatant_state(card)
            state.position = GridPosition(x=x, y=1)
            members.append(EncounterCombatant(
                combatant_id=name, side=side, position_ft=x * 5, state=state,
            ))
        owner, ally, foe = members
        setup = EncounterSetup(heroes=[foe], monsters=[owner, ally],
                               hero_total_levels=1, monster_total_cr="3", ruleset="2014")
        return owner, ally, foe, setup
    except Exception:
        logger.exception("Failed to build visible-ally test encounter.")
        raise
