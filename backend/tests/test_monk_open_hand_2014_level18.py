from __future__ import annotations

import pytest

from app.combat.conditions import attack_roll_condition_sources
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import expire_start_of_turn_conditions
from app.combat.timed_self_buffs import choose_timed_self_buff_action, resolve_timed_self_buff
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk = _member(build_kael_stillwater_2014(18), "kael", "heroes", 5)
    target = _member(build_karnok_stoneward_2014(18), "target", "monsters", 10)
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=18,
        monster_total_cr="0",
        ruleset="2014",
    )
    return monk, target, setup


def test_level18_snapshot_binds_empty_body_as_universal_timed_self_buff() -> None:
    hero = build_kael_stillwater_2014(18)
    profile = build_kael_stillwater_2014_profile(18)
    fingerprint = build_kael_2014_combat_profile(18)

    assert next(item for item in hero.resources if item.id == "ki").max_uses == 18
    assert fingerprint.resources == (("ki", 18), ("wholeness-of-body", 1))
    assert len(hero.timed_self_buff_actions) == 1
    action = hero.timed_self_buff_actions[0]
    assert action.id == "empty-body"
    assert action.name == "Empty Body"
    assert action.action_cost == "action"
    assert action.resource_id == "ki"
    assert action.resource_cost == 4
    assert action.duration_rounds == 10
    assert action.condition_ids == ["invisible"]
    assert set(action.damage_resistances) == {item for item in DamageType if item != DamageType.FORCE}
    assert DamageType.FORCE not in action.damage_resistances

    audit = next(item for item in profile.feature_audits if item.feature_id == "empty-body")
    assert audit.combat_relevant is True
    assert audit.automated is True


def test_empty_body_spends_action_and_ki_and_uses_universal_condition_and_resistance_state() -> None:
    monk, target, setup = _setup()
    begin_turn(monk.state)
    action = choose_timed_self_buff_action(monk)
    assert action is not None and action.id == "empty-body"

    event = resolve_timed_self_buff(1, 1, monk, action)

    assert event.feature_id == "empty-body"
    assert event.applied_condition_ids == ["invisible"]
    assert event.resource_remaining == 14
    assert monk.state.action_available is False
    assert "invisible" in monk.state.active_effect_ids
    effect = monk.state.timed_effects[0]
    assert effect.source_effect_id == "empty-body"
    assert effect.expires_round == 11
    assert effect.expiry_timing == "source_turn_start"
    assert adjusted_damage_amount(9, DamageType.FIRE, monk.state) == 4
    assert adjusted_damage_amount(9, DamageType.FORCE, monk.state) == 9

    attacker_advantage, _ = attack_roll_condition_sources(monk.state, target.state, 5)
    _, attacks_against_monk_disadvantage = attack_roll_condition_sources(target.state, monk.state, 5)
    assert attacker_advantage >= 1
    assert attacks_against_monk_disadvantage >= 1

    expired, _ = expire_start_of_turn_conditions(2, 11, monk, setup)
    assert expired and expired[0].feature_id == "empty-body"
    assert "invisible" not in monk.state.active_effect_ids
    assert adjusted_damage_amount(9, DamageType.FIRE, monk.state) == 9


def test_empty_body_is_illegal_without_four_ki() -> None:
    monk, _, _ = _setup()
    begin_turn(monk.state)
    ki = next(item for item in monk.state.resources if item.id == "ki")
    ki.current_uses = 3
    action = monk.state.template.timed_self_buff_actions[0]

    assert choose_timed_self_buff_action(monk) is None
    with pytest.raises(ValueError, match="Resource ki is unavailable"):
        resolve_timed_self_buff(1, 1, monk, action)
    assert monk.state.action_available is True
    assert ki.current_uses == 3
