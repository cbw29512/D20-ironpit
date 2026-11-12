"""Drow-family Darkness is one generic spell cast and a geometry-derived debuff."""
from __future__ import annotations

import logging

import pytest

from app.combat.concentration import end_concentration
from app.combat.conditions import attack_roll_condition_sources
from app.combat.suppression_zone_cast import (
    cast_suppression_zone, choose_suppression_zone_action,
)
from app.combat.suppression_zone_effects import (
    expire_suppression_zones, sync_suppression_zone_effects,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.visibility_rules import can_see
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id", ["drow", "drider"])
def test_darkness_cast_is_position_bound_debuff_and_expires_on_concentration(monster_id):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=5,
            state=build_combatant_state(template),
        )
        enemy = EncounterCombatant(
            combatant_id="enemy", side="heroes", position_ft=20,
            state=build_combatant_state(build_commoner()),
        )
        caster.state.position = GridPosition(x=1, y=7)
        enemy.state.position = GridPosition(x=4, y=7)
        setup = EncounterSetup(
            heroes=[enemy], monsters=[caster], ruleset="2014",
            hero_total_levels=1, monster_total_cr=card.challenge_rating,
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(caster.state)
        selected = choose_suppression_zone_action(caster, setup, "1:caster")
        assert selected is not None
        action, position = selected
        assert action.id == "darkness" and position == enemy.state.position
        event, _ = cast_suppression_zone(
            1, 1, caster, setup, action, position, "1:caster",
        )
        assert event.feature_id == "darkness" and "Darkness" in event.description
        assert any(x.id == "darkness" and x.current_uses == 0
                   for x in caster.state.resources)
        assert enemy.state.active_effect_ids.count("magical-darkness") == 1
        assert caster.state.concentration.effect_id == "darkness"
        assert not can_see(caster.state, enemy.state, 15)
        assert not can_see(enemy.state, caster.state, 15)
        advantage, disadvantage = attack_roll_condition_sources(
            caster.state, enemy.state, 15,
        )
        assert advantage > 0 and disadvantage > 0

        # Each sense is universal; no special creature-identity logic.
        seeing = caster.state.model_copy(deep=True)
        seeing.template = template.model_copy(update={"truesight_ft": 60})
        assert can_see(seeing, enemy.state, 15)
        devil_seeing = caster.state.model_copy(deep=True)
        devil_seeing.template = template.model_copy(update={
            "magical_darkness_sight_ft": 120,
        })
        assert can_see(devil_seeing, enemy.state, 15)
        devil_seeing.template = template.model_copy(update={
            "magical_darkness_sight_ft": 10,
        })
        assert not can_see(devil_seeing, enemy.state, 15)
        blind_seeing = caster.state.model_copy(deep=True)
        blind_seeing.template = template.model_copy(update={"blindsight_ft": 60})
        blind_seeing.active_effect_ids.append("blinded")
        assert can_see(blind_seeing, enemy.state, 15)

        # Moving outside the zone clears the per-target status, while a line
        # that still crosses the darkness remains visually obscured.
        enemy.state.position = GridPosition(x=10, y=7)
        sync_suppression_zone_effects(setup, 1)
        assert "magical-darkness" not in enemy.state.active_effect_ids
        assert not can_see(caster.state, enemy.state, 45)

        assert end_concentration(caster.state, [caster.state, enemy.state])
        assert not caster.state.visible_obscuration_zones
        assert not enemy.state.visible_obscuration_zones
        expire_suppression_zones(setup, 2)
        sync_suppression_zone_effects(setup, 2)
        assert not setup.suppression_zones
        assert can_see(caster.state, enemy.state, 45)
    except Exception:
        logger.exception("2014 Darkness generic fight lifecycle failed for %s.", monster_id)
        raise
