"""Source-neutral 2014 area-save ranking using all typed damage components."""
from __future__ import annotations

import pytest

from app.combat.area_save_actions import choose_area_save
from app.combat.printed_damage import save_mean_damage
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _member(combatant_id: str, side: str, x: int) -> EncounterCombatant:
    """Build real fight-local state, not a mocked damage resolver."""
    state = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    state.position = GridPosition(x=x, y=0)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
    )


@pytest.mark.parametrize("source_label", ["Mixed Blast", "Completely Renamed Power"])
def test_area_save_prefers_complete_typed_damage_without_name_dispatch(source_label: str) -> None:
    actor = _member("actor", "heroes", 0)
    target = _member("target", "monsters", 1)
    geometry = AreaTargeting(shape="emanation", origin="self", radius_ft=10)
    legacy = SavingThrowAction(
        id="legacy", name="Old Power", save_ability="dexterity", dc=12,
        range_ft=0, area=geometry,
        damage_dice_count=3, damage_dice_size=6, damage_type="fire",
    )
    typed = SavingThrowAction(
        id="typed", name=source_label, save_ability="dexterity", dc=12,
        range_ft=0, area=geometry,
        damage_components=[
            {"dice_count": 2, "dice_size": 10, "damage_type": "cold"},
            {"dice_count": 1, "dice_size": 4, "damage_type": "force"},
        ],
    )
    actor.state.template.saving_throw_actions = [legacy, typed]
    setup = EncounterSetup(
        heroes=[actor], monsters=[target], hero_total_levels=1,
        monster_total_cr="1", ruleset="2014",
        map_definition=BattleMapDefinition(
            id="typed-area-ranking", width_squares=10, height_squares=10,
        ),
    )
    assert save_mean_damage(legacy) == 10.5
    assert save_mean_damage(typed) == 13.5
    selected = choose_area_save(actor, setup)
    assert selected is not None
    assert selected[0].id == "typed"
    assert target.combatant_id in selected[1].target_ids
