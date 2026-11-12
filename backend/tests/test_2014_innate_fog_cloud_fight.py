"""2014 physical Fog Cloud: source-neutral placement, AI and sight lifecycle."""
from __future__ import annotations

import logging

import pytest

from app.combat.concentration import end_concentration
from app.combat.suppression_zone_cast import cast_suppression_zone, choose_suppression_zone_action
from app.combat.suppression_zone_effects import expire_suppression_zones, sync_suppression_zone_effects
from app.combat.state import begin_turn, build_combatant_state
from app.combat.visibility_rules import can_see
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id,once_daily", [("ice-mephit", True), ("cloud-giant", False)])
def test_2014_fog_cloud_avoids_waste_and_blocks_sight_only_while_active(monster_id, once_daily):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        original = card.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=5,
            state=build_combatant_state(template),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=20,
            state=build_combatant_state(build_commoner()),
        )
        caster.state.position = GridPosition(x=1, y=7)
        target.state.position = GridPosition(x=4, y=7)
        setup = EncounterSetup(
            heroes=[target], monsters=[caster], ruleset="2014",
            hero_total_levels=1, monster_total_cr=card.challenge_rating,
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(caster.state)
        # Mutual concealment would cancel its own attack-roll modifiers.
        assert choose_suppression_zone_action(caster, setup, "1:caster") is None
        target.state.template = target.state.template.model_copy(update={
            "spell_save_actions": [SpellSaveAction(
                id="synthetic-sight-save", name="Sight-Gated Save", level=1,
                range_ft=60, save_ability="wisdom", dc=12,
                damage_dice_count=1, damage_dice_size=6,
                damage_type="psychic", requires_target_sight=True,
            )],
        })
        selected = choose_suppression_zone_action(caster, setup, "1:caster")
        assert selected is not None
        action, center = selected
        assert action.id == "fog-cloud" and center == target.state.position
        event, _ = cast_suppression_zone(1, 1, caster, setup, action, center, "1:caster")
        assert event.feature_id == "fog-cloud" and "Fog Cloud" in event.description
        resource = next((r for r in caster.state.resources if r.id == "fog-cloud"), None)
        assert (resource.current_uses if resource else None) == (0 if once_daily else None)
        assert caster.state.concentration.effect_id == "fog-cloud"
        assert not can_see(caster.state, target.state, 15)
        assert not can_see(target.state, caster.state, 15)
        assert "blinded" not in target.state.active_effect_ids
        assert "deafened" not in target.state.active_effect_ids
        assert target.state.zone_damage_immunities == []
        assert "magical-darkness" not in target.state.active_effect_ids
        truesight = caster.state.model_copy(deep=True)
        truesight.template = template.model_copy(update={
            "truesight_ft": 120, "magical_darkness_sight_ft": 120,
        })
        assert not can_see(truesight, target.state, 15)
        blindsight = caster.state.model_copy(deep=True)
        blindsight.template = template.model_copy(update={"blindsight_ft": 120})
        assert can_see(blindsight, target.state, 15)
        assert end_concentration(caster.state, [caster.state, target.state])
        expire_suppression_zones(setup, 2)
        sync_suppression_zone_effects(setup, 2)
        assert not setup.suppression_zones
        assert can_see(caster.state, target.state, 15)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("2014 Fog Cloud fight failed for %s.", monster_id)
        raise
