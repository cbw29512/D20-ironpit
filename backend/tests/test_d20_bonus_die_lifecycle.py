from __future__ import annotations

import pytest

from app.combat.d20_bonus_dice import (
    consume_d20_bonus_die,
    eligible_d20_bonus_dice,
    expire_d20_bonus_dice,
    resolve_d20_bonus_die_grant,
)
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.content.bard_2014_inspiration import build_bardic_inspiration_2014
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.domain.events import DiceRoll
from app.domain.models import EncounterSelection, ResourceDefinition


def _setup():
    bard = build_karnok_stoneward_2014(5).model_copy(update={
        "id": "bard-fixture",
        "name": "Bard Fixture",
        "archetype": "Bard",
        "resources": [ResourceDefinition(id="bardic-inspiration", name="Bardic Inspiration", max_uses=3)],
        "d20_bonus_die_actions": [build_bardic_inspiration_2014(5)],
    })
    ally = build_karnok_stoneward_2014(5).model_copy(update={"id": "ally-fixture", "name": "Ally"})
    enemy = build_karnok_stoneward_2014(5).model_copy(update={"id": "enemy-fixture", "name": "Enemy"})
    return build_encounter_setup(EncounterSelection(
        hero_templates=[bard, ally],
        monster_templates=[enemy],
        starting_distance_ft=30,
    ))


def test_grant_spend_and_expire_are_fresh_fight_state() -> None:
    setup = _setup()
    bard, ally = setup.heroes
    action = bard.state.template.d20_bonus_die_actions[0]

    event = resolve_d20_bonus_die_grant(1, 1, bard, ally, action)
    assert event.feature_id == "bardic-inspiration"
    assert bard.state.resources[0].current_uses == 2
    grants = eligible_d20_bonus_dice(ally.state, "attack", 1)
    assert len(grants) == 1 and grants[0].dice_size == 8

    revised = consume_d20_bonus_die(
        ally.state,
        grants[0],
        DiceRoll(notation="1d20 + 5", rolls=[10], selected_roll=10, modifier=5, total=15),
        FixedDiceProvider([6]),
    )
    assert revised.total == 21
    assert ally.state.active_d20_bonus_dice == []

    resolve_d20_bonus_die_grant(2, 2, bard, ally, action)
    assert expire_d20_bonus_dice(ally.state, 101) == []
    assert expire_d20_bonus_dice(ally.state, 102) == ["bardic-inspiration"]


def test_same_source_cannot_stack_same_grant_on_recipient() -> None:
    setup = _setup()
    bard, ally = setup.heroes
    action = bard.state.template.d20_bonus_die_actions[0]
    resolve_d20_bonus_die_grant(1, 1, bard, ally, action)
    with pytest.raises(ValueError):
        resolve_d20_bonus_die_grant(2, 1, bard, ally, action)
