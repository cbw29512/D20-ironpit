"""Incoming spell danger shares actual spell legality, scoring and targeting."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.combat.replacement_form_spell_threat import single_enemy_spell_pressure
from app.combat.replacement_form_threat import incoming_attack_pressure
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _encounter(builder):
    source = builder(8)
    defender = EncounterCombatant(
        combatant_id="defender", side="heroes", position_ft=0,
        state=build_combatant_state(source),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy-caster", side="monsters", position_ft=10,
        state=build_combatant_state(source),
    )
    setup = EncounterSetup(
        heroes=[defender], monsters=[enemy], hero_total_levels=8,
        monster_total_cr="0", ruleset=source.ruleset,
    )
    return defender, enemy, setup


@pytest.mark.parametrize("builder", [
    build_thalen_greenbough_2014, build_thalen_greenbough_level,
])
def test_save_spell_preview_scores_only_defender_and_does_not_spend_resources(builder) -> None:
    defender, enemy, setup = _encounter(builder)
    spell = enemy.state.template.spell_save_actions[0]
    enemy.state.action_available = False
    enemy.state.bonus_action_available = False
    enemy.state.turn_terminated = True
    prior_resources = [(r.id, r.current_uses) for r in enemy.state.resources]
    choice = SimpleNamespace(
        action=spell, slot_level=spell.level,
        target_ids=(defender.combatant_id,), expected_damage=999,
    )

    def selected(member, received_setup, turn_key):
        assert member is not enemy
        assert member.state is not enemy.state
        assert member.state.action_available
        assert member.state.bonus_action_available
        assert not member.state.turn_terminated
        assert turn_key == "forecast:enemy-caster"
        assert received_setup is setup
        return choice

    with (
        patch("app.combat.replacement_form_spell_threat.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_spell_threat.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_spell_threat.choose_spell", side_effect=selected),
        patch("app.combat.replacement_form_spell_threat.save_spell_expected_damage", return_value=13) as score,
    ):
        assert single_enemy_spell_pressure(enemy, defender, setup) == 13
        assert score.call_count == 1
        choice.target_ids = ("another-hero",)
        assert single_enemy_spell_pressure(enemy, defender, setup) == 0

    assert not enemy.state.action_available
    assert not enemy.state.bonus_action_available
    assert enemy.state.turn_terminated
    assert [(r.id, r.current_uses) for r in enemy.state.resources] == prior_resources


def test_auto_hit_and_attack_target_require_the_defender() -> None:
    defender, enemy, setup = _encounter(build_thalen_greenbough_level)
    source = enemy.state.template
    enemy.state.template = source.model_copy(update={
        "spell_save_actions": [],
        "auto_hit_spell_actions": [SimpleNamespace(id="test-auto")],
        "spell_attack_actions": [SimpleNamespace(id="test-attack")],
        "concentration_repeat_save_actions": [],
    })
    own = SimpleNamespace(combatant_id=defender.combatant_id)
    another = SimpleNamespace(combatant_id="someone-else")
    with (
        patch("app.combat.replacement_form_spell_threat.choose_auto_hit_spell",
              return_value=SimpleNamespace(target=own, expected_damage=17)),
        patch("app.combat.replacement_form_spell_threat.choose_spell_attack",
              return_value=SimpleNamespace(target=another, expected_damage=100)),
    ):
        assert single_enemy_spell_pressure(enemy, defender, setup) == 17


def test_incapacitated_or_dead_caster_cannot_make_a_spell_threat() -> None:
    defender, enemy, setup = _encounter(build_thalen_greenbough_2014)
    with patch("app.combat.replacement_form_spell_threat.choose_spell") as chooser:
        enemy.state.is_dead = True
        assert single_enemy_spell_pressure(enemy, defender, setup) == 0
        chooser.assert_not_called()


def test_total_incoming_uses_highest_single_enemy_action_not_sum() -> None:
    defender, _enemy, setup = _encounter(build_thalen_greenbough_level)
    with (
        patch("app.combat.replacement_form_threat.single_enemy_pressure", return_value=8),
        patch("app.combat.replacement_form_threat.single_enemy_spell_pressure", return_value=23),
    ):
        assert incoming_attack_pressure(defender, setup) == 23
