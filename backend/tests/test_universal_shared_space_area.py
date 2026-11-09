"""Universal shared-square saving throw targeting, independent of named abilities."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.area_targeting import legal_area_placements, member_in_area_placement
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def member(name: str, side: str, x: int, y: int):
    state = build_combatant_state(build_demo_fighter().model_copy(
        update={"id": name, "name": name},
    ))
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=name, side=side, position_ft=0, state=state,
    )


def battle():
    actor = member("actor", "monsters", 3, 3)
    overlapping = member("overlapping", "heroes", 3, 3)
    adjacent = member("adjacent", "heroes", 4, 3)
    ally = member("ally", "monsters", 3, 3)
    setup = EncounterSetup(
        heroes=[overlapping, adjacent], monsters=[actor, ally],
        hero_total_levels=1, monster_total_cr="5", ruleset="2014",
        map_definition=BattleMapDefinition(
            id="same-space", width_squares=8, height_squares=8,
        ),
    )
    return actor, setup


def test_exact_shared_space_excludes_adjacent_and_tracks_allies():
    owner, setup = battle()
    area = AreaTargeting(shape="shared-space", origin="self")
    placements = legal_area_placements(owner, setup, area, 0)
    assert len(placements) == 1
    placed = placements[0]
    assert placed.target_ids == ("overlapping",)
    assert placed.friendly_ids == ("ally",)
    assert member_in_area_placement(owner, setup.heroes[0], area, placed)
    assert not member_in_area_placement(owner, setup.heroes[1], area, placed)


def test_generic_save_only_targets_same_space_and_respects_target_scope():
    owner, setup = battle()
    area = AreaTargeting(shape="shared-space", origin="self")
    damage_action = SavingThrowAction(
        id="source-neutral-crush", name="Renamed Compress",
        save_ability="strength", dc=15, range_ft=0, area=area,
        max_targets=20, damage_dice_count=2, damage_dice_size=8,
        damage_bonus=4, damage_type="bludgeoning",
    )
    enemy = legal_area_save_placements(owner, setup, damage_action)
    assert len(enemy) == 1 and enemy[0].target_ids == ("overlapping",)
    all_others = damage_action.model_copy(update={
        "id": "cross-side-effect", "target_scope": "all-other-creatures",
    })
    all_plans = legal_area_save_placements(owner, setup, all_others)
    assert len(all_plans) == 1
    assert set(all_plans[0].target_ids) == {"overlapping", "ally"}


def test_shared_space_rejects_fabricated_radius_and_wrong_origin():
    with pytest.raises(ValidationError):
        AreaTargeting(shape="shared-space", origin="self", radius_ft=5)
    with pytest.raises(ValidationError):
        AreaTargeting(shape="shared-space", origin="point")
    with pytest.raises(ValidationError):
        AreaTargeting(shape="shared-space", origin="self", length_ft=5)
