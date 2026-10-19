"""RAW target-scope regression: allegiances never override printed 'all other creatures'."""
from __future__ import annotations

import pytest

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.save_targets import validate_save_targets
from app.combat.state import build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import _compile_save
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _member(cid: str, side: str, x: int) -> EncounterCombatant:
    state = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    state.position = GridPosition(x=x, y=1)
    return EncounterCombatant(combatant_id=cid, side=side, position_ft=x * 5, state=state)


def _setup(actor, allies, enemies):
    return EncounterSetup(
        heroes=[actor, *allies], monsters=enemies, hero_total_levels=1,
        monster_total_cr="1", ruleset="2014",
        map_definition=BattleMapDefinition(id="all-others", width_squares=12, height_squares=12),
    )


def _action(scope="all-other-creatures"):
    return SavingThrowAction(
        id="source-agnostic-wave", name="Arbitrary Wave",
        save_ability="constitution", dc=1, range_ft=0,
        target_scope=scope,
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=30),
    )


def test_printed_all_other_creatures_hits_eligible_allies_and_enemies() -> None:
    actor = _member("actor", "heroes", 1)
    friend = _member("friend", "heroes", 2)
    foe = _member("foe", "monsters", 3)
    actor.state.template.saving_throw_actions = [_action()]
    setup = _setup(actor, [friend], [foe])
    choice = choose_area_save(actor, setup)
    assert choice is not None
    assert set(choice[1].target_ids) == {"friend", "foe"}
    events, sequence = resolve_area_save(1, 1, actor, setup, choice[0], choice[1], FixedDiceProvider([20, 20]))
    assert sequence == 3
    assert {event.target_id for event in events} == {"friend", "foe"}
    assert "actor" not in {event.target_id for event in events}
    assert actor.state.action_available is False


def test_an_all_other_creatures_action_can_hit_an_ally_without_enemy_exposure() -> None:
    actor = _member("actor", "heroes", 1)
    friend = _member("friend", "heroes", 2)
    actor.state.template.saving_throw_actions = [_action()]
    # Iron Pit requires an opposing roster member, even when none is in range.
    far_enemy = _member("far-enemy", "monsters", 11)
    setup = _setup(actor, [friend], [far_enemy])
    choice = choose_area_save(actor, setup)
    assert choice is not None
    assert choice[1].target_ids == ("friend",)
    events, _ = resolve_area_save(1, 1, actor, setup, choice[0], choice[1], FixedDiceProvider([20]))
    assert [event.target_id for event in events] == ["friend"]


def test_old_save_actions_remain_enemy_only_and_forged_self_is_illegal() -> None:
    actor = _member("actor", "heroes", 1)
    friend = _member("friend", "heroes", 2)
    foe = _member("foe", "monsters", 3)
    action = _action("enemies")
    actor.state.template.saving_throw_actions = [action]
    setup = _setup(actor, [friend], [foe])
    choice = choose_area_save(actor, setup)
    assert choice is not None
    assert choice[1].target_ids == ("foe",)
    with pytest.raises(ValueError, match="Illegal save-action target"):
        validate_save_targets(actor, setup, action, ("friend",), skip_range_check=True)
    with pytest.raises(ValueError, match="Illegal save-action target"):
        validate_save_targets(actor, setup, _action(), ("actor",), skip_range_check=True)


def test_immutable_card_contract_rejects_unknown_scope_and_compiles_valid_scope() -> None:
    definition = SaveCapabilityDefinition(
        id="renamed-non-banshee", name="Renamed Ability",
        save_ability="constitution", dc=13, range_ft=30,
        target_scope="all-other-creatures",
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=30),
    )
    assert _compile_save(definition).target_scope == "all-other-creatures"
    assert SaveCapabilityDefinition.model_validate(
        {**definition.model_dump(), "target_scope": "enemies"}
    ).target_scope == "enemies"
    with pytest.raises(ValueError):
        SaveCapabilityDefinition.model_validate(
            {**definition.model_dump(), "target_scope": "all-friends-only"}
        )
