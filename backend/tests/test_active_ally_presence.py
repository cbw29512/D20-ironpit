"""Live ally presence shares the existing universal combat eligibility rules."""

import logging

from app.combat.ally_context import has_active_ally
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_active_ally_presence_tracks_live_fight_state():
    try:
        source = next(monster for monster in load_monster_source_2014() if monster.id == "satyr")
        template = compile_combatant(adapt_basic_monster_2014(source))
        owner = EncounterCombatant(combatant_id="owner", side="monsters", state=build_combatant_state(template))
        ally = EncounterCombatant(combatant_id="ally", side="monsters", state=build_combatant_state(template))
        foe = EncounterCombatant(combatant_id="foe", side="heroes", state=build_combatant_state(template))
        setup = EncounterSetup(heroes=[foe], monsters=[owner, ally], hero_total_levels=1, monster_total_cr="1")
        assert has_active_ally(owner, setup)
        assert not has_active_ally(foe, setup)
        ally.state.current_hp = 0
        assert not has_active_ally(owner, setup)
        ally.state.current_hp = 1
        assert has_active_ally(owner, setup)
    except Exception:
        logger.exception("Live active-ally predicate regression failed")
        raise
