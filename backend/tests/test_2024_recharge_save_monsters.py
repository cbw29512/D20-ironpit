from __future__ import annotations

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.recharge import resolve_recharge_checks
from app.combat.state import build_combatant_state
from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import (
    complete_monster_limited_use_fingerprints,
    limited_use_issues,
)
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters import build_commoner
from app.content.monsters_recharge_save import build_hell_hound
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.recharge import RechargeRule


def _source_complete_hell_hound():
    templates = complete_monster_trait_fingerprints([build_hell_hound()])
    templates = complete_monster_limited_use_fingerprints(templates)
    return complete_monster_saving_throws(templates)[0]


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def test_hell_hound_recharge_save_matches_2024_source() -> None:
    hell_hound = _source_complete_hell_hound()
    row = next(row for row in load_monster_rows() if row["name"] == "Hell Hound")

    assert audit_monster_source(hell_hound, row) == []
    assert hell_hound.attack_action is not None
    assert len(hell_hound.attack_action.slots) == 2

    breath = hell_hound.saving_throw_actions[0]
    assert (breath.name, breath.save_ability, breath.dc) == ("Fire Breath", "dexterity", 12)
    assert breath.area is not None
    assert (breath.area.shape, breath.area.length_ft) == ("cone", 15)
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (5, 6, "fire")
    assert breath.success_damage == "half"
    assert breath.resource_id == "fire-breath"
    assert hell_hound.resources[0].max_uses == 1
    assert hell_hound.recharge_rules[0].minimum_roll == 5


def test_hell_hound_uses_shared_area_save_and_recharge_lifecycle() -> None:
    actor = _member(_source_complete_hell_hound(), "monster:hell-hound", "monsters", 1, 1)
    first = _member(build_commoner(), "hero:first", "heroes", 2, 1)
    second = _member(build_commoner(), "hero:second", "heroes", 3, 1)
    setup = EncounterSetup(
        heroes=[first, second],
        monsters=[actor],
        hero_total_levels=2,
        monster_total_cr="3",
        ruleset="2024",
        map_definition=BattleMapDefinition(id="hell-hound-area", width_squares=10, height_squares=10),
    )

    selected = choose_area_save(actor, setup)
    assert selected is not None
    action, placement = selected
    assert action.id == "srd-hell-hound-fire-breath"
    assert set(placement.target_ids) == {"hero:first", "hero:second"}

    events, sequence = resolve_area_save(
        1,
        1,
        actor,
        setup,
        action,
        placement,
        FixedDiceProvider([1, 2, 3, 4, 5, 1, 20]),
    )
    assert sequence == 3
    assert len(events) == 2
    assert actor.state.resources[0].current_uses == 0
    assert events[0].damage_components[0].rolls == [1, 2, 3, 4, 5]
    assert events[1].damage_components[0].rolls == [1, 2, 3, 4, 5]

    checks = resolve_recharge_checks(actor.state, FixedDiceProvider([5]))
    assert checks[0].restored is True
    assert actor.state.resources[0].current_uses == 1


def test_wrong_recharge_threshold_remains_fail_closed() -> None:
    hell_hound = _source_complete_hell_hound().model_copy(
        update={"recharge_rules": [RechargeRule(resource_id="fire-breath", minimum_roll=6)]}
    )
    row = next(row for row in load_monster_rows() if row["name"] == "Hell Hound")
    issues = limited_use_issues(hell_hound, row)
    assert any(issue.startswith("uncertified-limited-use:") for issue in issues)
