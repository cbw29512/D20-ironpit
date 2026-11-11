"""2014 source admission and generic planted-zone terrain lifecycle tests."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.combat import persistent_save_zone_resolution as zone_resolver
from app.combat.concentration import end_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.persistent_save_zone_cast import cast_save_zone
from app.combat.persistent_save_zone_resolution import expire_save_zones
from app.combat.state import begin_turn, build_combatant_state
from app.combat.temporary_terrain import destination_is_difficult_terrain
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)
SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from browser_template_serializer import _save_zone


def _member(template, combatant_id, side, x):
    try:
        member = EncounterCombatant(
            combatant_id=combatant_id, side=side, position_ft=x * 5,
            state=build_combatant_state(template),
        )
        member.state.position = GridPosition(x=x, y=7)
        return member
    except Exception:
        logger.exception("Could not construct generic actor %s.", combatant_id)
        raise


def test_2014_planetar_composes_damage_zone_and_healing_without_special_resolver(monkeypatch):
    try:
        source = next(x for x in load_monster_source_2014() if x.id == "planetar")
        before = source.model_dump_json()
        assert basic_blockers_2014(source) == ()
        template = compile_combatant(adapt_basic_monster_2014(source))
        assert len(template.attack_action.slots) == 2
        assert template.healing_actions[0].name == "Healing Touch"
        assert any(x.id == "healing-touch" and x.max_uses == 4 for x in template.resources)
        zone = next(x for x in template.persistent_save_zone_actions if x.id == "insect-plague")
        assert zone.level == 5 and zone.dc == 20
        assert zone.triggers == ["appear", "enter", "end_turn"]
        assert zone.damage_dice_count == 4 and zone.damage_dice_size == 10
        assert zone.creates_difficult_terrain and zone.lightly_obscured
        assert zone.target_policy == "all" and zone.success_damage == "half"
        serialized = _save_zone(zone)
        assert serialized["createsDifficultTerrain"]
        assert serialized["lightlyObscured"]
        assert serialized["resourceId"] == "insect-plague"

        caster = _member(template, "angel", "monsters", 1)
        target = _member(build_commoner().model_copy(update={"max_hp": 100}),
                         "target", "heroes", 9)
        setup = EncounterSetup(
            heroes=[target], monsters=[caster],
            hero_total_levels=1, monster_total_cr="16", ruleset="2014",
            map_definition=build_standard_iron_pit_map(),
        )
        begin_turn(caster.state)
        monkeypatch.setattr(zone_resolver, "resolve_saving_throw",
                            lambda *_args, **_kwargs: (None, False))
        events, _ = cast_save_zone(
            1, 1, caster, setup, zone, target.state.position,
            "1:angel", FixedDiceProvider([1, 1, 1, 1]),
        )
        assert events[0].feature_id == "insect-plague"
        assert len(setup.save_zones) == 1
        terrain = setup.temporary_terrain_zones
        assert len(terrain) == 1
        assert terrain[0].persistent_zone_id == setup.save_zones[0].zone_id
        assert destination_is_difficult_terrain(terrain, target, target.state.position)
        assert setup.save_zones[0].lightly_obscured
        assert any(x.id == "insect-plague" and x.current_uses == 0
                   for x in caster.state.resources)
        assert end_concentration(caster.state, [caster.state, target.state])
        expire_save_zones(setup, 2)
        assert not setup.save_zones and not setup.temporary_terrain_zones
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("Planetar shared 2014 zone lifecycle certification failed.")
        raise
