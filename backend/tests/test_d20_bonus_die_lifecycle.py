from __future__ import annotations

import pytest

from app.combat.d20_bonus_dice import (
    consume_d20_bonus_die,
    eligible_d20_bonus_dice,
    expire_d20_bonus_dice,
    resolve_d20_bonus_die_grant,
)
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_bard import build_lyra_silverstring_level
from app.content.bard_2014_inspiration import build_bardic_inspiration_2014
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.domain.events import DiceRoll
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import ResourceDefinition


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
    return EncounterSetup(
        heroes=[
            EncounterCombatant(combatant_id="hero-bard", side="heroes", position_ft=0, state=build_combatant_state(bard)),
            EncounterCombatant(combatant_id="hero-ally", side="heroes", position_ft=20, state=build_combatant_state(ally)),
        ],
        monsters=[
            EncounterCombatant(combatant_id="monster-enemy", side="monsters", position_ft=30, state=build_combatant_state(enemy)),
        ],
        hero_total_levels=10,
        monster_total_cr="5",
        ruleset="2014",
    )


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

    begin_turn(bard.state)
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


def test_restoration_conversion_spends_slot_only_after_grant_legality() -> None:
    bard_template = build_lyra_silverstring_level(5)
    ally_template = build_karnok_stoneward_2014(5).model_copy(
        update={"id": "font-ally", "name": "Font Ally"}
    )
    enemy_template = build_karnok_stoneward_2014(5).model_copy(
        update={"id": "font-enemy", "name": "Font Enemy"}
    )
    bard = EncounterCombatant(
        combatant_id="font-bard",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(bard_template),
    )
    ally = EncounterCombatant(
        combatant_id="font-ally",
        side="heroes",
        position_ft=20,
        state=build_combatant_state(ally_template),
    )
    enemy = EncounterCombatant(
        combatant_id="font-enemy",
        side="monsters",
        position_ft=20,
        state=build_combatant_state(enemy_template),
    )
    inspiration = next(item for item in bard.state.resources if item.id == "bardic-inspiration")
    slot = next(item for item in bard.state.resources if item.id == "spell-slot-1")
    inspiration.current_uses = 0
    slot.current_uses = 1
    action = bard.state.template.d20_bonus_die_actions[0]

    with pytest.raises(ValueError):
        resolve_d20_bonus_die_grant(1, 1, bard, enemy, action)
    assert slot.current_uses == 1
    assert inspiration.current_uses == 0

    event = resolve_d20_bonus_die_grant(2, 1, bard, ally, action)
    assert slot.current_uses == 0
    assert inspiration.current_uses == 0
    assert len(ally.state.active_d20_bonus_dice) == 1
    assert "Font of Inspiration" in event.description


@pytest.mark.parametrize("round_number, succeeds", [(1, True), (101, False)])
def test_nested_concentration_save_uses_current_round(round_number, succeeds):
    from app.combat.concentration import start_concentration, resolve_concentration_damage

    setup = _setup()
    bard, ally = setup.heroes
    resolve_d20_bonus_die_grant(1, 1, bard, ally, bard.state.template.d20_bonus_die_actions[0])
    ally.state.current_round = round_number
    start_concentration(ally.state, ally.combatant_id, "test-concentration", 1)
    result = resolve_concentration_damage(ally.state, 1, FixedDiceProvider([1, 8]))
    assert result.succeeded is succeeds
    assert (ally.state.concentration is not None) is succeeds
    assert ally.state.active_d20_bonus_dice == []
    assert build_combatant_state(ally.state.template).current_round is None
