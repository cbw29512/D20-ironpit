import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.group_healing import choose_group_healing_targets, resolve_group_healing
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import HealingAction


def _hero(index: int, position: int) -> EncounterCombatant:
    template = build_karnok_stoneward()
    member = EncounterCombatant(
        combatant_id=f"hero-{index}",
        side="heroes",
        position_ft=position,
        state=build_combatant_state(template),
    )
    member.state.current_hp = 1
    return member


def _setup() -> EncounterSetup:
    heroes = [_hero(0, 0), _hero(1, 80), _hero(2, 95)]
    heroes[0].state.current_hp = heroes[0].state.template.max_hp
    monster = EncounterCombatant(
        combatant_id="monster-0",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(build_goblin_warrior()),
    )
    return EncounterSetup(
        heroes=heroes,
        monsters=[monster],
        hero_total_levels=3,
        monster_total_cr="1/4",
        starting_distance_ft=30,
    )


def _area_heal() -> HealingAction:
    return HealingAction(
        id="area-heal",
        name="Area Heal",
        action_cost="action",
        range_ft=60,
        area_radius_ft=30,
        target_mode="self_or_ally",
        max_targets=6,
        dice_count=1,
        dice_size=8,
        healing_bonus=0,
    )


def test_area_group_healing_uses_cast_point_range_plus_radius() -> None:
    setup = _setup()
    healer, reachable, too_far = setup.heroes
    targets = choose_group_healing_targets(healer, setup, _area_heal())

    assert reachable in targets
    assert too_far not in targets


def test_area_group_healing_resolution_requires_one_legal_placement() -> None:
    setup = _setup()
    healer, reachable, too_far = setup.heroes
    action = _area_heal()

    events, sequence = resolve_group_healing(
        1,
        1,
        healer,
        [reachable],
        action,
        FixedDiceProvider([8]),
        setup=setup,
    )
    assert sequence == 2
    assert events[0].target_id == reachable.combatant_id

    with pytest.raises(ValueError, match="legal healing area"):
        resolve_group_healing(
            2,
            1,
            healer,
            [too_far],
            action,
            FixedDiceProvider([8]),
            setup=setup,
        )
