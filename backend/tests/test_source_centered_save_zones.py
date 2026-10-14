from __future__ import annotations

from app.domain.persistent_save_zones import PersistentSaveZoneAction


def test_source_centered_save_zone_is_explicit_and_opt_in() -> None:
    base = dict(
        id="source-cloud", name="Source Cloud", level=0, cast_range_ft=0,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    assert PersistentSaveZoneAction(**base).center_on_source is False
    action = PersistentSaveZoneAction(**base, center_on_source=True)
    assert action.center_on_source
    assert action.model_dump()["center_on_source"] is True

def test_browser_serializer_only_exports_explicit_source_centering() -> None:
    import sys
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from browser_template_serializer import _save_zone
    from app.domain.persistent_save_zones import PersistentSaveZoneAction

    params = dict(
        id="generic-cloud", name="Generic Cloud", level=0, cast_range_ft=0,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    assert "centerOnSource" not in _save_zone(PersistentSaveZoneAction(**params))
    assert _save_zone(PersistentSaveZoneAction(**params, center_on_source=True))["centerOnSource"] is True


def test_source_centered_zone_chooses_caster_square_and_rejects_other_centers() -> None:
    import pytest
    from app.combat.persistent_save_zone_cast import choose_save_zone_center, cast_save_zone
    from app.combat.state import begin_turn, build_combatant_state
    from app.content.arena_map import build_standard_iron_pit_map
    from app.content.monsters import build_commoner
    from app.domain.encounters import EncounterCombatant, EncounterSetup
    from app.domain.grid import GridPosition
    from app.domain.persistent_save_zones import PersistentSaveZoneAction

    action = PersistentSaveZoneAction(
        id="generic-cloud", name="Generic Cloud", level=0, cast_range_ft=0,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], failed_save_condition_id="poisoned",
        center_on_source=True,
    )
    template = build_commoner()
    caster = EncounterCombatant(
        combatant_id="caster", side="heroes", position_ft=5,
        state=build_combatant_state(template),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy", side="monsters", position_ft=15,
        state=build_combatant_state(template),
    )
    caster.state.position = GridPosition(x=1, y=7)
    enemy.state.position = GridPosition(x=3, y=7)
    setup = EncounterSetup(
        heroes=[caster], monsters=[enemy], hero_total_levels=1,
        monster_total_cr="0", ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )
    begin_turn(caster.state)
    assert choose_save_zone_center(caster, setup, action) == caster.state.position
    with pytest.raises(ValueError, match="centered on its source"):
        cast_save_zone(1, 1, caster, setup, action, enemy.state.position, "1:caster", None)
    assert setup.save_zones == []
