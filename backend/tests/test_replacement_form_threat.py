"""Source-neutral conservative attack pressure for survival-shape AI."""
from __future__ import annotations

from unittest.mock import patch
from types import SimpleNamespace

from app.combat.printed_damage import weapon_mean_damage
from app.combat.replacement_form_threat import (
    incoming_attack_pressure, pressure_may_be_lethal, single_enemy_pressure,
)
from app.combat.replacement_form_offense import defer_emergency_form_for_spell
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _actors():
    defender_template = build_thalen_greenbough_level(8)
    enemy_template = build_thalen_greenbough_2014(8)
    attack = enemy_template.weapon_attack
    sequence = AttackActionDefinition(
        id="two-hits", name="Two Hits",
        slots=[AttackActionSlot(attack_ids=[attack.id]),
               AttackActionSlot(attack_ids=[attack.id])],
    )
    enemy_template = enemy_template.model_copy(update={
        "attack_action": sequence, "saving_throw_actions": [], "speed_ft": 30,
    })
    defender = EncounterCombatant(
        combatant_id="caster", side="heroes", position_ft=0,
        state=build_combatant_state(defender_template),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy", side="monsters", position_ft=15,
        state=build_combatant_state(enemy_template),
    )
    setup = EncounterSetup(
        heroes=[defender], monsters=[enemy], hero_total_levels=8,
        monster_total_cr="0", ruleset="2024",
    )
    return defender, enemy, setup, weapon_mean_damage(attack)


def test_printed_multiattack_lookahead_covers_reach_and_movement() -> None:
    defender, enemy, setup, hit = _actors()
    assert single_enemy_pressure(enemy, defender) == 2 * hit
    assert incoming_attack_pressure(defender, setup) == 2 * hit
    enemy.position_ft = 150
    assert single_enemy_pressure(enemy, defender) == 0
    enemy.state.is_dead = True
    assert incoming_attack_pressure(defender, setup) == 0


def test_lethal_pressure_checks_temporary_hp_and_avoids_fake_certainty() -> None:
    assert pressure_may_be_lethal(10, 0, 10)
    assert not pressure_may_be_lethal(10, 5, 10)
    assert not pressure_may_be_lethal(10, 0, 0)
    assert not pressure_may_be_lethal(0, 0, 20)


def test_imminent_lethal_attack_overrides_stronger_spell_choice() -> None:
    defender, enemy, setup, _hit = _actors()
    defender.state.current_hp = int(defender.state.template.max_hp * 0.25)
    form = defender.state.template.replacement_form_actions[0]
    spell = SimpleNamespace(
        action=SimpleNamespace(id="offense", action_cost="action"),
        expected_damage=90,
    )
    with (
        patch("app.combat.replacement_form_offense.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell", return_value=spell),
        patch("app.combat.replacement_form_offense.choose_concentration_repeat_save", return_value=None),
        patch("app.combat.replacement_form_offense.incoming_attack_pressure", return_value=999),
    ):
        assert not defer_emergency_form_for_spell(defender, setup, form, "1:caster")
    with (
        patch("app.combat.replacement_form_offense.choose_auto_hit_spell", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell_attack", return_value=None),
        patch("app.combat.replacement_form_offense.choose_spell", return_value=spell),
        patch("app.combat.replacement_form_offense.choose_concentration_repeat_save", return_value=None),
        patch("app.combat.replacement_form_offense.incoming_attack_pressure", return_value=0),
    ):
        assert defer_emergency_form_for_spell(defender, setup, form, "1:caster")
