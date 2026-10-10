"""Live ally presence shares the existing universal combat eligibility rules."""

import logging

from app.combat.ally_context import has_active_ally, has_visible_active_ally_within
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def test_active_ally_presence_tracks_live_fight_state(monkeypatch):
    try:
        source = next(monster for monster in load_monster_source_2014() if monster.id == "satyr")
        template = compile_combatant(adapt_basic_monster_2014(source))
        owner = EncounterCombatant(combatant_id="owner", side="monsters", position_ft=0, state=build_combatant_state(template))
        ally = EncounterCombatant(combatant_id="ally", side="monsters", position_ft=5, state=build_combatant_state(template))
        foe = EncounterCombatant(combatant_id="foe", side="heroes", position_ft=30, state=build_combatant_state(template))
        setup = EncounterSetup(heroes=[foe], monsters=[owner, ally], hero_total_levels=1, monster_total_cr="1")
        assert has_active_ally(owner, setup)
        assert not has_active_ally(foe, setup)
        ally.state.current_hp = 0
        assert not has_active_ally(owner, setup)
        ally.state.current_hp = 1
        assert has_active_ally(owner, setup)
        # A present but incapacitated ally cannot satisfy an active-ally trigger.
        monkeypatch.setattr(
            "app.combat.ally_context.is_incapacitated",
            lambda state: state is ally.state,
        )
        assert not has_active_ally(owner, setup)
    except Exception:
        logger.exception("Live active-ally predicate regression failed")
        raise


def test_visible_active_ally_has_range_and_sight_requirements(monkeypatch):
    from types import SimpleNamespace
    from app.combat.ally_context import has_visible_active_ally_within

    state = lambda: SimpleNamespace(is_alive=True, is_dead=False, current_hp=10)
    owner = EncounterCombatant(combatant_id="owner", side="monsters", position_ft=0, state=state())
    ally = EncounterCombatant(combatant_id="ally", side="monsters", position_ft=25, state=state())
    foe = EncounterCombatant(combatant_id="foe", side="heroes", position_ft=10, state=state())
    setup = EncounterSetup(heroes=[foe], monsters=[owner, ally], hero_total_levels=1, monster_total_cr="1")
    monkeypatch.setattr("app.combat.ally_context.is_incapacitated", lambda _: False)
    monkeypatch.setattr("app.combat.condition_rules.can_see", lambda *_: True)
    assert has_visible_active_ally_within(owner, setup, 30)
    assert not has_visible_active_ally_within(owner, setup, 20)
    monkeypatch.setattr("app.combat.condition_rules.can_see", lambda *_: False)
    assert not has_visible_active_ally_within(owner, setup, 30)
