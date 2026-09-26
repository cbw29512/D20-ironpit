from __future__ import annotations

from app.combat.concentration import end_concentration
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.demo import build_goblin_warrior
from app.content.shared_invisibility_spells_2014 import greater_invisibility_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    lyra = EncounterCombatant(
        combatant_id="lyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_lyra_silverstring_2014(8)),
    )
    goblin = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=30,
        state=build_combatant_state(build_goblin_warrior()),
    )
    return lyra, goblin, EncounterSetup(
        heroes=[lyra],
        monsters=[goblin],
        hero_total_levels=8,
        monster_total_cr="1/4",
        ruleset="2014",
    )


def test_greater_invisibility_uses_existing_invisible_condition_and_concentration() -> None:
    spell = greater_invisibility_2014()

    assert spell.level == 4
    assert spell.action_cost == "action"
    assert spell.range_ft == 5
    assert spell.duration_minutes == 1
    assert spell.target_policy == "friendly"
    assert spell.condition_ids == ["invisible"]
    assert spell.concentration is True


def test_level_eight_lyra_uses_greater_invisibility_as_free_opening_buff() -> None:
    lyra, goblin, setup = _setup()
    slot = next(item for item in lyra.state.resources if item.id == "spell-slot-4")

    events, sequence = prepare_opening_buffs(setup)

    assert sequence == 2
    assert [event.feature_id for event in events] == ["greater-invisibility"]
    assert lyra.state.opening_buff_id == "greater-invisibility"
    assert lyra.state.action_available is True
    assert lyra.state.bonus_action_available is True
    assert slot.current_uses == 1
    assert lyra.state.concentration is not None
    assert lyra.state.concentration.effect_id == "greater-invisibility"
    assert "invisible" in lyra.state.active_effect_ids
    effect = next(item for item in lyra.state.timed_effects if item.effect_id == "invisible")
    assert effect.source_effect_id == "greater-invisibility"
    assert effect.applied_round == 0
    assert effect.expires_round == 11
    assert effect.source_is_magical is True

    ended = end_concentration(
        lyra.state,
        [lyra.state, goblin.state],
    )
    assert ended is True
    assert lyra.state.concentration is None
    assert "invisible" not in lyra.state.active_effect_ids
    assert not any(item.source_effect_id == "greater-invisibility" for item in lyra.state.timed_effects)
