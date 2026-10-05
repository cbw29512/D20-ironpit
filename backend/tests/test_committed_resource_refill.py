from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.delayed_resource_refill import resolve_delayed_resource_refill_end_turn
from app.combat.delayed_resource_refill_policy import (
    arena_may_start_committed_resource_refill,
    has_printed_damaging_option,
)
from app.combat.delayed_resource_refill_start import start_delayed_resource_refill
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.warlock_fiend_2024_runtime import build_varek_ashenmark_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(level: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=f"varek-{level}",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_varek_ashenmark_2024(level)),
    )


def _resource(actor: EncounterCombatant, resource_id: str):
    return next(item for item in actor.state.resources if item.id == resource_id)


def _start_rite(actor: EncounterCombatant, *, pact_id: str, spent: int) -> None:
    _resource(actor, pact_id).current_uses = spent
    events, _ = start_delayed_resource_refill(1, 1, actor)
    assert events[0].feature_id == "magical-cunning"
    assert _resource(actor, "magical-cunning").current_uses == 0
    assert actor.state.delayed_resource_refills[0].completes_round == 11


def test_end_turn_does_not_auto_start_magical_cunning() -> None:
    varek = _member(2)
    _resource(varek, "spell-slot-1").current_uses = 0

    events, _ = resolve_delayed_resource_refill_end_turn(1, 1, varek)

    assert events == []
    assert varek.state.delayed_resource_refills == []
    assert _resource(varek, "magical-cunning").current_uses == 1


def test_magical_cunning_locks_unrelated_actions_until_the_minute_ends() -> None:
    varek = _member(2)
    _start_rite(varek, pact_id="spell-slot-1", spent=0)

    assert is_available(varek.state, "action") is False
    assert is_available(varek.state, "bonus_action") is False
    assert is_available(varek.state, "reaction") is True
    assert varek.state.movement_remaining_ft == 0

    begin_turn(varek.state)
    assert is_available(varek.state, "action") is False
    assert is_available(varek.state, "bonus_action") is False
    assert varek.state.movement_remaining_ft == 0
    assert is_available(varek.state, "reaction") is True
    assert _resource(varek, "spell-slot-1").current_uses == 0

    for round_number in range(2, 11):
        events, _ = resolve_delayed_resource_refill_end_turn(2, round_number, varek)
        assert events == []
        assert _resource(varek, "spell-slot-1").current_uses == 0

    events, _ = resolve_delayed_resource_refill_end_turn(2, 11, varek)
    assert events[0].feature_id == "magical-cunning"
    assert "completes Magical Cunning" in events[0].description
    assert _resource(varek, "spell-slot-1").current_uses == 1
    assert varek.state.delayed_resource_refills == []

    begin_turn(varek.state)
    assert is_available(varek.state, "action") is True


def test_incapacitated_warlock_does_not_restore_slots() -> None:
    varek = _member(2)
    _start_rite(varek, pact_id="spell-slot-1", spent=0)
    varek.state.is_unconscious = True

    events, _ = resolve_delayed_resource_refill_end_turn(2, 4, varek)

    assert "stops Magical Cunning" in events[0].description
    assert _resource(varek, "spell-slot-1").current_uses == 0
    assert varek.state.delayed_resource_refills == []


def test_damage_alone_does_not_cancel_the_rite() -> None:
    varek = _member(2)
    _start_rite(varek, pact_id="spell-slot-1", spent=0)
    varek.state.current_hp = max(1, varek.state.current_hp - 8)

    events, _ = resolve_delayed_resource_refill_end_turn(2, 4, varek)

    assert events == []
    assert varek.state.delayed_resource_refills[0].completes_round == 11
    assert _resource(varek, "spell-slot-1").current_uses == 0


def test_arena_does_not_start_the_rite_while_damage_exists() -> None:
    varek = _member(2)
    _resource(varek, "spell-slot-1").current_uses = 0

    assert has_printed_damaging_option(varek) is True
    assert arena_may_start_committed_resource_refill(varek) is False


def test_combat_turn_keeps_fighting_instead_of_starting_the_rite() -> None:
    varek = _member(2)
    _resource(varek, "spell-slot-1").current_uses = 0
    enemy_template = build_commoner().model_copy(update={"id": "dummy", "max_hp": 40})
    enemy = EncounterCombatant(
        combatant_id="dummy",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(enemy_template),
    )
    varek.state.position = GridPosition(x=2, y=8)
    enemy.state.position = GridPosition(x=14, y=8)
    setup = EncounterSetup(
        heroes=[varek],
        monsters=[enemy],
        hero_total_levels=2,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )

    events, _ = resolve_combat_turn(1, 1, varek, enemy, setup, FixedDiceProvider([15, 8, 4, 4, 4, 4]))

    assert varek.state.delayed_resource_refills == []
    assert _resource(varek, "magical-cunning").current_uses == 1
    assert any(item.feature_id == "magical-cunning" for item in events) is False


def test_level_twenty_restores_all_pact_slots_only_after_the_full_minute() -> None:
    varek = _member(20)
    rule = varek.state.template.progression_features.delayed_resource_refill
    assert rule is not None
    assert rule.restore_mode == "max"
    _start_rite(varek, pact_id="spell-slot-5", spent=1)

    events, _ = resolve_delayed_resource_refill_end_turn(2, 10, varek)
    assert events == []
    assert _resource(varek, "spell-slot-5").current_uses == 1

    events, _ = resolve_delayed_resource_refill_end_turn(2, 11, varek)
    assert _resource(varek, "spell-slot-5").current_uses == 4
    assert varek.state.delayed_resource_refills == []
