from __future__ import annotations

from unittest.mock import Mock

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import DiceProvider, FixedDiceProvider
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _no_rolls():
    try:
        dice = Mock(spec=DiceProvider)
        dice.roll.side_effect = AssertionError("This gate must not roll dice.")
        return dice
    except Exception:
        raise


def _pit_fiend_source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "pit-fiend")
    except Exception as exc:
        raise AssertionError("Missing repaired 2014 Pit Fiend source.") from exc


def _aura():
    try:
        action, = condition_auras_from_source(_pit_fiend_source().source_traits, "2014")
        return action
    except Exception:
        raise


def _fixture(source_id: str = "source-a", source_position: int = 20):
    try:
        action = _aura()
        source_template = build_demo_fighter().model_copy(update={
            "id": "renamed-dread-source",
            "name": "Renamed Dread Source",
            "kind": "monster",
            "ruleset": "2014",
            "timed_self_buff_actions": [action],
        })
        target_template = build_demo_fighter().model_copy(update={
            "id": "renamed-target",
            "name": "Renamed Target",
            "ruleset": "2014",
        })
        source = EncounterCombatant(
            combatant_id=source_id, side="monsters", position_ft=source_position,
            state=build_combatant_state(source_template),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=0,
            state=build_combatant_state(target_template),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[source], hero_total_levels=1,
            monster_total_cr="20", ruleset="2014",
        )
        return setup, source, target
    except Exception:
        raise


def test_failure_applies_frightened_until_target_next_turn_and_resets_next_fight():
    try:
        setup, source, target = _fixture()
        events, sequence = resolve_target_turn_start_emanations(
            1, 1, target, setup, FixedDiceProvider([1]),
        )
        assert len(events) == 1 and events[0].save_dc == 21
        assert events[0].applied_condition_ids == ["frightened"]
        effect, = target.state.timed_effects
        assert effect.effect_id == "frightened"
        assert effect.expiry_timing == "target_turn_start"
        ended, _ = resolve_target_condition_timing(
            sequence, 1, target, "target_turn_start", _no_rolls(), setup,
        )
        assert ended[0].removed_condition_ids == ["frightened"]
        assert build_combatant_state(target.state.template).timed_effects == []
        assert source.state.template.timed_self_buff_actions == [_aura()]
    except Exception:
        raise


def test_success_immunity_is_source_scoped_and_survives_rounds_not_new_fights():
    try:
        setup, source, target = _fixture()
        passed, sequence = resolve_target_turn_start_emanations(
            1, 1, target, setup, FixedDiceProvider([20]),
        )
        assert passed[0].save_succeeded is True
        assert has_source_effect_immunity(target.state, "fear-aura", source.combatant_id)
        repeated, _ = resolve_target_turn_start_emanations(
            sequence, 500, target, setup, _no_rolls(),
        )
        assert repeated == []

        other = source.model_copy(update={
            "combatant_id": "source-b",
            "state": build_combatant_state(source.state.template),
        })
        setup.monsters.append(other)
        second, _ = resolve_target_turn_start_emanations(
            sequence, 2, target, setup, FixedDiceProvider([1]),
        )
        assert len(second) == 1 and second[0].actor_id == "source-b"
        fresh = build_combatant_state(target.state.template)
        assert not has_source_effect_immunity(fresh, "fear-aura", source.combatant_id)
    except Exception:
        raise


def test_range_incapacitation_condition_immunity_and_death_gate_without_rolls():
    try:
        for reason in ("range", "incapacitated", "condition-immune", "dead", "ally"):
            setup, source, target = _fixture()
            if reason == "range":
                source.position_ft = 25
            elif reason == "incapacitated":
                source.state.active_effect_ids.append("stunned")
            elif reason == "condition-immune":
                target.state.template = target.state.template.model_copy(
                    update={"condition_immunities": ["frightened"]},
                )
            elif reason == "dead":
                source.state.is_dead = True
                source.state.is_alive = False
            else:
                source.side = "heroes"
            events, sequence = resolve_target_turn_start_emanations(
                1, 1, target, setup, _no_rolls(),
            )
            assert (events, sequence) == ([], 1)
            assert target.state.timed_effects == []
    except Exception:
        raise
