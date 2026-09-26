from __future__ import annotations

from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.content.bard_2014_countercharm import countercharm_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id: str, side: str, position: int, *, countercharm: bool = False):
    template = build_commoner().model_copy(update={
        "id": f"{combatant_id}-template",
        "name": combatant_id.title(),
        "ruleset": "2014",
        "timed_self_buff_actions": [countercharm_2014()] if countercharm else [],
    })
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_timed_feature_can_use_the_one_free_opening_buff_before_initiative() -> None:
    bard = _member("bard", "heroes", 0, countercharm=True)
    ally = _member("ally", "heroes", 20)
    enemy = _member("enemy", "monsters", 40)
    setup = EncounterSetup(
        heroes=[bard, ally],
        monsters=[enemy],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
    )

    events, sequence = prepare_opening_buffs(setup)

    assert sequence == 2
    assert len(events) == 1
    assert events[0].round_number == 0
    assert events[0].feature_id == "countercharm"
    assert bard.state.opening_buff_id == "countercharm"
    assert bard.state.action_available is True
    assert bard.state.bonus_action_available is True
    assert bard.state.reaction_available is True
    assert bard.state.timed_effects[0].expires_round == 1
    assert bard.state.timed_effects[0].expiry_timing == "source_turn_end"


def test_opening_buff_is_single_use_for_the_fight() -> None:
    bard = _member("bard", "heroes", 0, countercharm=True)
    enemy = _member("enemy", "monsters", 40)
    setup = EncounterSetup(
        heroes=[bard],
        monsters=[enemy],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
    )

    first, sequence = prepare_opening_buffs(setup)
    second, final_sequence = prepare_opening_buffs(setup, sequence)

    assert [event.feature_id for event in first] == ["countercharm"]
    assert second == []
    assert final_sequence == sequence
