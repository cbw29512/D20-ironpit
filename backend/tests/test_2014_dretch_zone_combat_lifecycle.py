"""Real fight-state regression for a source-bound moving 2014 monster zone."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.combat import persistent_save_zone_resolution as resolver
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.persistent_save_zone_cast import cast_save_zone
from app.combat.persistent_save_zone_windows import resolve_save_zone_window
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def test_dretch_cloud_cast_poison_expiry_and_resource_reset(monkeypatch) -> None:
    source = next(m for m in load_monster_source_2014() if m.id == "dretch")
    # Compile source-bound behavior without falsely declaring whole-monster admission.
    with patch("app.content.monster_definition_adapter_2014.basic_blockers_2014", return_value=()):
        template = compile_combatant(adapt_basic_monster_2014(source))
    assert len(template.persistent_save_zone_actions) == 1
    action = template.persistent_save_zone_actions[0]

    caster = EncounterCombatant(
        combatant_id="caster", side="monsters", position_ft=5,
        state=build_combatant_state(template),
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=10,
        state=build_combatant_state(build_commoner()),
    )
    caster.state.position = GridPosition(x=1, y=7)
    target.state.position = GridPosition(x=2, y=7)
    setup = EncounterSetup(
        heroes=[target], monsters=[caster], hero_total_levels=1,
        monster_total_cr="1/4", ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )

    begin_turn(caster.state)
    cast_events, _ = cast_save_zone(
        1, 1, caster, setup, action, caster.state.position, "1:caster", None,
    )
    assert cast_events[0].feature_id == "fetid-cloud"
    assert len(setup.save_zones) == 1 and setup.save_zones[0].follows_source
    resource = next(item for item in caster.state.resources if item.id == "fetid-cloud")
    assert resource.current_uses == 0

    monkeypatch.setattr(resolver, "resolve_saving_throw", lambda *_: (None, False))
    save_events, _ = resolve_save_zone_window(
        2, 1, target, setup, None, "1:target", "start_turn",
    )
    assert save_events[0].applied_condition_ids == ["poisoned"]
    assert "poisoned" in target.state.active_effect_ids
    effect = next(item for item in target.state.timed_effects if item.effect_id == "poisoned")
    assert effect.expiry_timing == "target_turn_start"
    assert effect.suppress_reactions
    assert effect.control_limits.action_bonus_exclusive

    expiry_events, _ = resolve_target_condition_timing(
        3, 2, target, "target_turn_start", None, setup,
    )
    assert expiry_events[0].removed_condition_ids == ["poisoned"]
    assert "poisoned" not in target.state.active_effect_ids
    begin_turn(caster.state)
    with pytest.raises(ValueError, match="Resource fetid-cloud is unavailable"):
        cast_save_zone(4, 2, caster, setup, action, caster.state.position, "2:caster", None)
    assert len(setup.save_zones) == 1
